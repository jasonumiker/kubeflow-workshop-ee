S3URI="s3://bucket/path/"

aws s3 cp source.zip $S3URI/source.zip
aws s3 cp cloud9-ide-instance.template.yaml $S3URI/cloud9-ide-instance.template.yaml
aws s3 cp bootstrap.sh $S3URI/bootstrap.sh
aws s3 sync functions $S3URI/functions/