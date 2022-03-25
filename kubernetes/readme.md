# Github action runner controller Helm chart

Github action runner controller can be installed using regular k8s manifest or using an helm chart. For this demonstration I have chosen to use the helm chart as it is the easiest to setup, maintain and upgrade.

:warning: Helm will not update CRDs which will need to be manually upgraded after each app version upgrade. (c.f. [action-runner-controller doc](https://github.com/actions-runner-controller/actions-runner-controller/blob/master/charts/actions-runner-controller/docs/UPGRADING.md#steps))

## Instalation

### cert-manager

By default, actions-runner-controller uses cert-manager for certificate management of Admission Webhook. Simply apply the manifests provided in `./cert-manager`. These are simply the manifests available at https://github.com/cert-manager/cert-manager/releases/download/v1.7.2/cert-manager.yaml the basic configuration is good enough for this poc. 

```
kubectl apply -f ./cert-manager/cert-manager.yaml
```

### Authentication

Github App offers slightly increased API quotas and it's the authentication method I'm going to use. It's also easier to setup a centralized webhook endpoint rather than per repo.

For this demonstration, **I won't be setting up the webhook right away** as I'll know the endpoint to use later on in the process.

The steps to create the github App are explained [here](https://github.com/actions-runner-controller/actions-runner-controller#deploying-using-github-app-authentication)

### Action Runner Controller helm chart

This is far from an ideal setup at the moment. For simplicity sake the webhook server service is deployed as a NodePort so we don't have to deal with application load balancer or anything like this for the time being.

Additionally the `action-runner-controller/controller/values.yaml` file is using placeholders for obvious reason but in a prod environment the real values could be encrypted in your gitops solution with something like [sops](https://github.com/mozilla/sops).

Add the actions-runner-controller helm repo.

```
helm repo add actions-runner-controller https://actions-runner-controller.github.io/actions-runner-controller
helm repo update
```

Update the `action-runner-controller/controller/values.yaml` file with the required values:

- **github_app_id**
- **github_app_installation_id**
- **github_app_private_key**
- **github_webhook_secret_token**

Then run the install command:

```
helm upgrade --install --namespace actions-runner-system --create-namespace --wait -f action-runner-controller/controller/values.yaml actions-runner-controller actions-runner-controller/actions-runner-controller
```

Once the controller is deployed we can move on to create the actual runners.

### Setting up the webhook

:warning: The current setup for the webhook is bad. It requires manual setup, it's not secure and it's janky. It's simply a quick way to get started with the most important part which is the autoscalling of runners. It will improved further down the line.

The last step is setting up the webhook to actually trigger the autoscalling when a workflow starts or complete.

Take note of the NodePort on which the webhook server is exposed (e.g. `30123` in the example below).

```
kubectl -n actions-runner-system get svc

NAME                                              TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)        AGE
actions-runner-controller-github-webhook-server   NodePort    10.100.1.1   <none>        80:30123/TCP   120m
actions-runner-controller-metrics-service         ClusterIP   10.100.1.2   <none>        8443/TCP       120m
actions-runner-controller-webhook                 ClusterIP   10.100.1.3   <none>        443/TCP        120m
```

From the AWS console, take note of the public IP of your EKS worker node then edit the security group attached to it and allow inbound traffic onto port `30123`.

Now on the setting page for the Github App, activate the webhook and in the webhook url field enter `http://<node_ip>:30123`. Finally navigate the the `Permission & events` page then in the `Subscribe to events` section, select `Workflow job`.


### Runners

There are multiple ways to create action runners. Once again for simplicity sake I will be creating the most basic one targeting a single repository.

To let the runners autoscale up and down we need two things. First we need to **not** include the `replicas:` setting in the runner configuration. Secondly we need to back it with a HorizontalRunnerAutoscaller (hra).

There is an [example runner](./runners/single-repo-runnerDeployment.yaml) provided in this repo. Simply update the targeted repository with your own and apply it in your cluster.

```
kubectl apply -f action-runner-controller/runners/single-repo-runnerDeployment.yaml
```
