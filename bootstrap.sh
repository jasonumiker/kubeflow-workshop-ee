#!/bin/bash
echo Setting up required prerequisites
pip install --upgrade pip awscli
curl --silent --location -o /usr/local/bin/kubectl "https://amazon-eks.s3.us-west-2.amazonaws.com/1.16.8/2020-04-16/bin/linux/amd64/kubectl"
chmod +x /usr/local/bin/kubectl
curl --silent --location -o /usr/local/bin/aws-iam-authenticator "https://amazon-eks.s3.us-west-2.amazonaws.com/1.16.8/2020-04-16/bin/linux/amd64/aws-iam-authenticator"
chmod +x /usr/local/bin/aws-iam-authenticator
curl --silent --location "https://github.com/weaveworks/eksctl/releases/download/latest_release/eksctl_Linux_amd64.tar.gz" | tar xz -C /tmp
mv -v /tmp/eksctl /usr/local/bin
chmod +x /usr/local/bin/eksctl
sudo yum -y install jq gettext bash-completion
export ACCOUNT_ID=$(aws sts get-caller-identity --output text --query Account)
export AWS_REGION=$(curl -s 169.254.169.254/latest/dynamic/instance-identity/document | jq -r '.region')
echo "export ACCOUNT_ID=${ACCOUNT_ID}" | tee -a ~/.bashrc
echo "export AWS_REGION=${AWS_REGION}" | tee -a ~/.bashrc
aws configure set default.region ${AWS_REGION}
aws configure get default.region
aws eks update-kubeconfig --name cluster