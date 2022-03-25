# Kubernetes on AWS

## Install eksctl

To install `eksctl` on linux, run

```
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin
```

For other OS check the [eksctl doc](https://eksctl.io/introduction/#installation).

# Create a Kubernetes cluster

The provided cluster configuration will create a k8s cluster in the `eu-west-1` region (feel free to change it to another region of your choice) with a single spot `t3.medium` worker node.

Create the cluster by running

```
eksctl create cluster -f eksctl/cluster.yaml --kubeconfig ~/.kube/config-action-runner-poc
export KUBECONFIG=~/.kube/config-action-runner-poc
```

If for whatever reason the command fails to complete, the cluster might still come up but you won't get the kubeconfig created locally. In which case you can create it using this command.

```
eksctl utils write-kubeconfig --cluster=action-runner-POC --kubeconfig ~/.kube/config-action-runner-poc
```

Once you're done testing the solution the cluster can be removed by running 

```
eksctl delete cluster --name action-runner-POC
```
