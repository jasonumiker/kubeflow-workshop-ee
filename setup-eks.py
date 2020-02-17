from aws_cdk import (
    aws_codebuild as codebuild,
    aws_iam as iam,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_codebuild as codebuild,
    aws_ec2 as ec2,
    aws_cloud9 as cloud9,
    aws_s3 as s3,
    core
)
import os

class EnvironmentStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        eks_vpc = ec2.Vpc(
            self, "VPC",
            cidr="10.0.0.0/16"
        )
        
        self.node.apply_aspect(core.Tag("kubernetes.io/cluster/cluster", "shared"))

        eks_vpc.private_subnets[0].node.apply_aspect(core.Tag("kubernetes.io/role/internal-elb", "1"))
        eks_vpc.private_subnets[1].node.apply_aspect(core.Tag("kubernetes.io/role/internal-elb", "1"))
        eks_vpc.public_subnets[0].node.apply_aspect(core.Tag("kubernetes.io/role/elb", "1"))
        eks_vpc.public_subnets[1].node.apply_aspect(core.Tag("kubernetes.io/role/elb", "1"))

        # Create IAM Role For CodeBuild and Cloud9
        codebuild_role = iam.Role(
            self, "BuildRole",
            assumed_by=iam.CompositePrincipal(
                iam.ServicePrincipal("codebuild.amazonaws.com"),
                iam.ServicePrincipal("ec2.amazonaws.com")
            ),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess")
            ]
        )

        instance_profile = iam.CfnInstanceProfile(
            self, "InstanceProfile",
            roles=[codebuild_role.role_name]            
        )

        # Create CodeBuild PipelineProject
        build_project = codebuild.PipelineProject(
            self, "BuildProject",
            role=codebuild_role,
            build_spec=codebuild.BuildSpec.from_source_filename("buildspec.yml")
        )

        # Create CodePipeline
        pipeline = codepipeline.Pipeline(
            self, "Pipeline",
        )

        # Create Artifact
        artifact = codepipeline.Artifact()

        # S3 Source Bucket
        source_bucket = s3.Bucket.from_bucket_attributes(
            self, "SourceBucket",
            bucket_arn=core.Fn.join("",["arn:aws:s3:::ee-assets-prod-",core.Fn.ref("AWS::Region")])
        )

        # Add Source Stage
        pipeline.add_stage(
            stage_name="Source",
            actions=[
                codepipeline_actions.S3SourceAction(
                    action_name="S3SourceRepo",
                    bucket=source_bucket,
                    bucket_key="modules/2cae1f20008d4fc5aaef294602649b98/v2/source.zip",
                    output=artifact,
                    trigger=codepipeline_actions.S3Trigger.NONE
                )
            ]
        )

        # Add CodeBuild Stage
        pipeline.add_stage(
            stage_name="Deploy",
            actions=[
                codepipeline_actions.CodeBuildAction(
                    action_name="CodeBuildProject",
                    project=build_project,
                    type=codepipeline_actions.CodeBuildActionType.BUILD,
                    input=artifact,
                    environment_variables={
                        'PublicSubnet1ID': codebuild.BuildEnvironmentVariable(value=eks_vpc.public_subnets[0].subnet_id),
                        'PublicSubnet2ID': codebuild.BuildEnvironmentVariable(value=eks_vpc.public_subnets[1].subnet_id),
                        'PrivateSubnet1ID': codebuild.BuildEnvironmentVariable(value=eks_vpc.private_subnets[0].subnet_id),
                        'PrivateSubnet2ID': codebuild.BuildEnvironmentVariable(value=eks_vpc.private_subnets[1].subnet_id),
                        'AWS_DEFAULT_REGION': codebuild.BuildEnvironmentVariable(value=self.region),
                        'INSTANCEPROFILEID': codebuild.BuildEnvironmentVariable(value=instance_profile.ref)
                    }
                )
            ]
        )

        cloud9_instance = cloud9.CfnEnvironmentEC2(
            self, 'Cloud9Instance',
            instance_type="t2.micro",
            automatic_stop_time_minutes=30,
            subnet_id=eks_vpc.public_subnets[0].subnet_id,
            owner_arn=core.Fn.join("",["arn:aws:iam::",core.Fn.ref("AWS::AccountId"),":role/TeamRole"])
        )

        pipeline.node.add_dependency(eks_vpc)
        pipeline.node.add_dependency(cloud9_instance)
        cloud9_instance.node.add_dependency(eks_vpc)

app = core.App()
environment_stack = EnvironmentStack(app, "EnvironmentStack")
app.synth()