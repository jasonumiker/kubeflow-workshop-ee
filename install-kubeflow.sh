#!/bin/bash
set +e
curl --silent --location "https://github.com/kubeflow/kubeflow/releases/download/v0.7.0/kfctl_v0.7.0_linux.tar.gz" | tar xz -C /tmp
sudo mv -v /tmp/kfctl /usr/local/bin
export CONFIG_URI=https://raw.githubusercontent.com/kubeflow/manifests/v0.7-branch/kfdef/kfctl_aws.0.7.0.yaml
export AWS_CLUSTER_NAME=cluster
export KF_NAME=${AWS_CLUSTER_NAME}
export BASE_DIR=~/environment
export KF_DIR=${BASE_DIR}/${KF_NAME}
STACK_NAME=$(eksctl get nodegroup --cluster cluster -o json | jq -r '.[].StackName')
ROLE_NAME=$(aws cloudformation describe-stack-resources --stack-name $STACK_NAME | jq -r '.StackResources[] | select(.ResourceType=="AWS::IAM::Role") | .PhysicalResourceId')
echo "export ROLE_NAME=${ROLE_NAME}" | tee -a ~/.bash_profile
mkdir -p ${KF_DIR}
cd ${KF_DIR}
kfctl build -V -f ${CONFIG_URI}
export CONFIG_FILE=${KF_DIR}/kfctl_aws.0.7.0.yaml
cd /tmp
wget https://github.com/kubeflow/manifests/archive/v0.7-branch.tar.gz
tar -xvf v0.7-branch.tar.gz
cd $KF_DIR
sed -i -e 's/kubeflow-aws/'"$AWS_CLUSTER_NAME"'/' ${CONFIG_FILE}
sed -i "s@us-west-2@$AWS_REGION@" ${CONFIG_FILE}
sed -i "s@https://github.com/kubeflow/manifests/archive/c0e81bedec9a4df8acf568cc5ccacc4bc05a3b38.tar.gz@file:///tmp/manifests-0.7-branch@" ${CONFIG_FILE}
sed -i "s@eksctl-cluster-nodegroup-ng-a2-NodeInstanceRole-xxxxxxx@$ROLE_NAME@" ${CONFIG_FILE}
rm -rf kustomize
kfctl apply -V -f ${CONFIG_FILE}