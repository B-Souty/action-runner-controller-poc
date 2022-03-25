# Github Action Runner Controller on Kubernetes **- WIP -**

## How does it work

Github App subscribed to `Workflow job` events installed on user/organization repositories.

Queued workflow trigger a webhook which the github app send to the configures webhook endpoint.

The webhook server component of the Action Runner Controller (ARC) receives the webhook.

The runner manager component of the ARC trigger a scale up of the a corresponding Runner defined by a CRD back by an HorizontalRunnerAutoscaler.
