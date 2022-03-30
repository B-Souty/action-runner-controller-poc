# Github Action Runners

## Motivation

The goal of this repo is investigating a solution to deploy github action runners able to autoscale based on workflows needs. The solution I've chosen for this is the Action Runer Controller (ARC) on kubernetes.

For the purpose of this demonstration I will be setting up a temporary kubernetes cluster on AWS using EKS.

### TODO

This repo is still very much a work in progress and needs to be improved in several places.

- Fix an issue where the Dind sidecar container prevents runner pods from being terminated.
- Fix an issue where runers are being re-created once a workflow is completed (they get automatically terminated after 5 minutes).
- Improve webhook server endpoint. (e.g. [AWS load balancer controller](https://github.com/kubernetes-sigs/aws-load-balancer-controller))
- Test different ways to setup runners (Org, runner groups, ...)

## Setting up the infrastructure

### EKS cluster

I will be seting up a single worker node cluster using [eksctl](https://eksctl.io/)

To deploy the cluster, navigate to the `./AWS/eksctl` directory and create the cluster with the command below:

```
eksctl create cluster -f cluster.yaml --kubeconfig ~/.kube/config-action-runner-poc
```

More info [here](./AWS/readme.md).

## Deploy the Action Runer Controller on Kubernetes

1. [Deploy cert-manager](./kubernetes/readme.md#cert-manager).
2. [Create a Github App](./kubernetes/readme.md#Authentication).
3. [Update ARC chart values](./kubernetes/readme.md#Action-Runner-Controller-helm-chart).
4. [deploy the ARC chart](./kubernetes/readme.md#Action-Runner-Controller-helm-chart).
5. [Allow ARC webhook server NodePort in the security group](./kubernetes/readme.md#Allow-inbound-traffic-to-the-webhook-server).
6. [Add webhook to the Github App](./kubernetes/readme.md#Setting-up-the-webhook).
7. [Create a runner](./kubernetes/readme.md#Runners).

## Utilities

A [script](./utils/list-aws-resources/list-aws-resources.py) is provided to list all AWS resources deployed as part of this POC. A guide is available [here](./utils/readme.md).
