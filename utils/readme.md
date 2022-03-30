# Misc utilities

## Listing AWS resources

### aws cli

You can easily list **most** resources deployed for the purpose of this poc by running the following command

```
aws resourcegroupstaggingapi get-resources --tag-filters "Key=poc,Values=action-runner-controller"
```

This will list all resources bearing the `poc: action-runner-controller` tag along with all their tags. You can use a different key:value pair based on the tags specified in the eksctl [cluster.yaml](../AWS/eksctl/cluster.yaml#L6-L7) config file.

Additionally, you can use [jq](https://stedolan.github.io/jq/) to only list the `arn` of all those resources

```
aws resourcegroupstaggingapi get-resources --tag-filters "Key=poc,Values=action-runner-controller" | jq ' .ResourceTagMappingList[].ResourceARN'
```

**_Note_**: The issue with this solution is that a few resources do not get that tag added (e.g. network interfaces, launch templates, ...). The python script below fixes that shortcoming.

### Python script

This script allows to easily list all resources that makes up the k8s cluster for this poc including those missing in the aws cli command. It uses tags and resource ID of the correctly discovered resources to figure out other resources making up the cluster.

#### Authentication

The script will use env variable (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`) to authenticate the request to AWS.

#### Basic usage

First install the dependencies using the `list-aws-resources/requirements.txt` file with `pip install -r requirements.txt` or simply `pip install boto3 click`.

Running the `list-aws-resources.py` script with no parameters will list the ARN only of all resources related to **any** eks cluster running in your account.

```
python list-aws-resources.py

arn:aws:eks:eu-west-1:123456789012:cluster/action-runner-POC
arn:aws:ec2:eu-west-1:123456789012:internet-gateway/igw-0a8707065b80038d7
arn:aws:ec2:eu-west-1:123456789012:subnet/subnet-0316f43b46c0b32ab
arn:aws:ec2:eu-west-1:123456789012:subnet/subnet-09873be91975bf9da
arn:aws:ec2:eu-west-1:123456789012:vpc/vpc-06ef59ec25ba80c68
.....
```

#### Filtering

You can filter down to specific clusters using either a comma separated list of cluster names or using a tag filter.

```
# list resources related to specific clusters
python list-aws-resources.py --cluster-names action-runner-POC
python list-aws-resources.py --cluster-names clusterA,clusterB,clusterC

# list resources related to clusters with specific tag
python list-aws-resources.py --filter-tag '{"Key": "poc": "Value": "action-runner-controller"}'
```

#### Format Output

By default the script will simply return the list of ARNs of the resource making up the cluster.

You can get the same list as with `aws resourcegroupstaggingapi get-resources` by using the `--raw` option

```
python list-aws-resources.py --raw
```

The `--rich` option will format the list to separate resources by aws services and type of resource (e.g. `ec2.instance`, `ec2.volume`, `eks.cluster`, ...).

Finally the `--tags` option which only has an effect with the `--rich` option will simply add the tags to the rich output.
