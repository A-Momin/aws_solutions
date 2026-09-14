import boto3, botocore
from botocore.exceptions import ClientError
import os, time, json, io, zipfile
from datetime import date
from dotenv import load_dotenv


from misc import load_from_yaml, save_to_yaml
import iam, s3, lf, rds, networking, ec2

load_dotenv(".env")
# boto3.setup_default_session(profile_name="AMominNJ")

ACCOUNT_ID        = os.environ['AWS_ACCOUNT_ID_ROOT']
REGION            = os.environ['AWS_DEFAULT_REGION']
VPC_ID            = os.environ['AWS_DEFAULT_VPC']
SECURITY_GROUP_ID = os.environ['AWS_DEFAULT_SG_ID']
SUBNET_IDS        = SUBNET_IDS = os.environ["AWS_DEFAULT_SUBNET_IDS"].split(":")
SUBNET_ID         = SUBNET_IDS[0]

# ============================================================================
emr_client = boto3.client('emr', region_name=REGION)
# ============================================================================


def create_emr_cluster(Name, LogUri, ReleaseLabel, Ec2SubnetId):
    cluster_id = emr_client.run_job_flow(
        Name=Name,  # Name of the EMR cluster
        LogUri=LogUri,  # S3 bucket for log storage
        ReleaseLabel=ReleaseLabel, #"emr-6.12.0",  # EMR release version
        Instances={
            "InstanceGroups": [
                {
                    "InstanceRole": "MASTER",
                    "InstanceType": "m5.xlarge",
                    "InstanceCount": 1,
                    "Market": "ON_DEMAND"
                },
                {
                    "InstanceRole": "CORE",
                    "InstanceType": "m5.xlarge",
                    "InstanceCount": 2,
                    "Market": "ON_DEMAND"
                },
                {
                    "InstanceRole": "TASK",
                    "InstanceType": "m5.xlarge",
                    "InstanceCount": 1,  # Optional: Add if task nodes are required
                    "Market": "ON_DEMAND"
                }
            ],
            "Ec2KeyName": "AMominNJ",  # EC2 key pair for SSH access
            "KeepJobFlowAliveWhenNoSteps": True,
            "TerminationProtected": False,
            "Ec2SubnetId": Ec2SubnetId,  # Replace with your subnet ID
            # "HadoopVersion": "2.10.1",  # Optional: Hadoop version
        },
        Applications=[
            {"Name": "Hadoop"},
            {"Name": "Spark"},
            {"Name": "Hive"},
            {"Name": "Hue"},
            {"Name": "JupyterHub"},
        ],
        VisibleToAllUsers=True,
        JobFlowRole="EMR_EC2_DefaultRole",  # IAM role for EMR EC2 instances
        ServiceRole="EMR_DefaultRole",  # IAM role for EMR service
        Tags=[
            {"Key": "Environment", "Value": "Development"},
            {"Key": "Project", "Value": "EMR_DataEngineering"}
        ],
        AutoScalingRole="EMR_AutoScaling_DefaultRole",  # Optional: For auto-scaling
        ScaleDownBehavior="TERMINATE_AT_TASK_COMPLETION",  # Scale-down behavior
        StepConcurrencyLevel=1,  # Optional: Max concurrent steps
        # Configurations=[
        #     {
        #         "Classification": "spark-defaults",
        #         "Properties": {"spark.executor.memory": "4G"}
        #     },
        #     {
        #         "Classification": "hadoop-env",
        #         "Configurations": [
        #             {
        #                 "Classification": "export",
        #                 "Properties": {"JAVA_HOME": "/usr/lib/jvm/java-1.8.0"}
        #             }
        #         ]
        #     }
        # ],
        # BootstrapActions=[
        #     {
        #         "Name": "CustomBootstrap",
        #         "ScriptBootstrapAction": {
        #             "Path": "s3://emr-bkt/scripts/bootstrap.sh",
        #             "Args": ["arg1", "arg2"]
        #         }
        #     }
        # ],
        # Steps=[
        #     {
        #         "Name": "ExampleStep",
        #         "ActionOnFailure": "CONTINUE",
        #         "HadoopJarStep": {
        #             "Jar": "command-runner.jar",
        #             "Args": ["spark-submit", "--deploy-mode", "cluster", "--class", "org.apache.spark.examples.SparkPi", "s3://path-to-your-jar/spark-examples.jar", "10"]
        #         }
        #     }
        # ],
        # CustomAmiId="ami-xxxxxxxx",  # Optional: Custom AMI ID if required
        # SecurityConfiguration="MySecurityConfig",  # Optional: Security configuration
        # ManagedScalingPolicy={
        #     "ComputeLimits": {
        #         "UnitType": "InstanceFleetUnits",
        #         "MinimumCapacityUnits": 1,
        #         "MaximumCapacityUnits": 10,
        #         "MaximumOnDemandCapacityUnits": 5,
        #         "MaximumCoreCapacityUnits": 5
        #     }
        # },
        # KerberosAttributes={  # Optional: For Kerberos authentication
        #     "Realm": "EC2.INTERNAL",
        #     "KdcAdminPassword": "my-secret-password",
        #     "CrossRealmTrustPrincipalPassword": "cross-realm-password",
        #     "ADDomainJoinUser": "admin",
        #     "ADDomainJoinPassword": "password"
        # }
    )['JobFlowId']

    return cluster_id