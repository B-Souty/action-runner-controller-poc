import json
import re

import boto3
import click


class ARN(object):

    def __init__(self, arn, tags=None):
        self.full_arn = arn
        self.tags = {t["Key"]: t["Value"] for t in tags}

        pattern = "arn:aws:(?P<service>.*?):(?:(?P<region>.*?))?:(?:(?P<account_id>.*?)):(?:(?P<resource>.*?))/?(?P<resource_id>.*?)$"
        match = re.match(pattern, self.full_arn)

        if match:
            self.service = match.group("service")
            self.region = match.group("region")
            self.account_id = match.group("account_id")
            self.resource = match.group("resource")
            self.resource_id = match.group("resource_id")

        if "/" in self.resource_id:
            decomposed_id = self.resource_id.split("/")
            self.resource_id = decomposed_id.pop(-1)
            self.resource = "/".join(decomposed_id)

    def __str__(self):
        return self.full_arn


def format_output(data, rich=False, tags=False):

    if tags:
        raise SyntaxError("Can't use tags option with simple output.")
    output = "\n".join([r.full_arn for r in data])

    if rich:
        to_output = {}
        for r in data:
            if not to_output.get(r.service):
                to_output[r.service] = {}
            if not to_output[r.service].get(r.resource):
                to_output[r.service][r.resource] = []
            if tags:
                to_output[r.service][r.resource].append({r.resource_id: r.tags})
                continue
            to_output[r.service][r.resource].append(r.resource_id)
        output = json.dumps(to_output, indent=2)

    return output


def get_aws_resources():

    client = boto3.client('resourcegroupstaggingapi')

    response = client.get_resources(
        ResourcesPerPage=100,
    )

    resources = response.get("ResourceTagMappingList")

    while response.get("PaginationToken"):
        response = client.get_resources(
            PaginationToken=response.get("PaginationToken"),
            ResourcesPerPage=100,
        )
        resources.extend(response.get("ResourceTagMappingList"))

    return resources


def select_cluster_resources(resources, cluster_names=None, tag_filter=None):

    data = [ARN(r["ResourceARN"], r["Tags"]) for r in resources]

    if tag_filter and (not tag_filter.get("Key") or not tag_filter.get("Value")):
        raise SyntaxError('Filter malformed. Should be in the form {"Key": "some_key", "Value": "some_value"}')

    if not cluster_names:
        cluster_names = []
        for d in data:
            if d.service == "eks" and d.resource == "cluster":
                if tag_filter and not d.tags.get(tag_filter["Key"]) == tag_filter["Value"]:
                    continue
                cluster_names.append(d.tags.get("alpha.eksctl.io/cluster-name"))

    cluster_resources = [d for d in data for cluster_name in cluster_names if cluster_name in d.tags.values()]
    cluster_nodes = [c for c in cluster_resources if c.service == "ec2" and c.resource == "instance"]

    for r in set(data) - set(cluster_resources):
        if r.tags.get("node.k8s.amazonaws.com/instance_id") in [n.resource_id for n in cluster_nodes]:
            cluster_resources.append(r)

    return cluster_resources


@click.command()
@click.option("--cluster-names", default="", help="The EKS cluster names to retrieve the list of resources.")
@click.option('--tag-filter', default="", help="Select clusters based on tag instead or in addition of cluster names.")
@click.option('--rich', is_flag=True, default=False, help='Rich format output.')
@click.option('--tags', is_flag=True, default=False, help='Include tags to rich format.')
@click.option('--raw', is_flag=True, default=False, help='Raw output from aws.')
def main(cluster_names, tag_filter, rich, tags, raw):

    if tag_filter:
        try:
            tag_filter = json.loads(tag_filter)
        except json.decoder.JSONDecodeError:
            raise SyntaxError('Filter malformed. Should be in the form {"Key": "some_key", "Value": "some_value"}')

    resources = get_aws_resources()

    if cluster_names:
        cluster_names = cluster_names.split(",")
    cluster_resources = select_cluster_resources(resources, cluster_names=cluster_names, tag_filter=tag_filter)

    if raw:
        print(json.dumps([r for r in resources if r.get("ResourceARN") in [c.full_arn for c in cluster_resources]], indent=2))
        exit(0)

    print(format_output(cluster_resources, rich=rich, tags=tags))


if __name__ == '__main__':
    main()
