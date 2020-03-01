If deploying through EE then use `EnvironmentStack.template.json` as well as optionally as well as upload both `sources.zip` and `cloud9-ide-instance.yaml` to S3 and update the paths to indicate where if the paths in the template become unavailable.

If not deploying through EE then use `EnvironmentStack-notEE.template.json` - which doesn't set the team OwnerArn instead using the Role of whomever deploys the whole Stack.
