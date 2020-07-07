If deploying through EE then use `EnvironmentStack.template.json` as well as optionally as well as upload `sources.zip`, `cloud9-ide-instance.template.yaml` and the functions folder to S3 and update the paths to indicate the path for the artifacts.

There is also `EnvironmentStack-boostrap.template.json` which is that but also runs bootstrap.sh on the Cloud9 to try to help set that up with the prerequiste steps for eksworkshop.com. The problem is that I can't see how to turn off AWS Managed Credentials and so you still need to flip that off before you can run some of them like `aws eks update-kubeconfig` etc.

If not deploying through EE then use `EnvironmentStack-notEE.template.json` - which doesn't set the team OwnerArn instead using the Role of whomever deploys the whole Stack but is otherwise the same.
