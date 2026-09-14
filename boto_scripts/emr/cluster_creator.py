#!/usr/bin/env python3
"""
AWS EMR Cluster Creator with Comprehensive Configuration Options

This script creates an AWS EMR cluster with all possible customization options,
following AWS best practices for security, monitoring, and cost optimization.

Author: AWS Data Engineering Team
Version: 1.0.0
"""

import boto3
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError, NoCredentialsError
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("emr_cluster_creation.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class EMRClusterCreator:
    """
    Comprehensive EMR Cluster Creator with all configuration options
    """

    def __init__(self, aws_profile: Optional[str] = None, region: str = "us-east-1"):
        """
        Initialize EMR Cluster Creator

        Args:
            aws_profile: AWS profile name (optional, uses default if not provided)
            region: AWS region for cluster creation
        """
        self.region = region
        self.aws_profile = aws_profile

        # Initialize AWS clients
        try:
            if aws_profile:
                session = boto3.Session(profile_name=aws_profile)
            else:
                session = boto3.Session()

            self.emr_client = session.client("emr", region_name=region)
            self.ec2_client = session.client("ec2", region_name=region)
            self.iam_client = session.client("iam", region_name=region)
            self.s3_client = session.client("s3", region_name=region)

            logger.info(f"Initialized AWS clients for region: {region}")

        except NoCredentialsError:
            logger.error(
                "AWS credentials not found. Please configure your credentials."
            )
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error initializing AWS clients: {str(e)}")
            sys.exit(1)

    def create_security_groups(self, vpc_id: str, cluster_name: str) -> Dict[str, str]:
        """
        Create security groups for EMR cluster

        Args:
            vpc_id: VPC ID where cluster will be created
            cluster_name: Name of the EMR cluster

        Returns:
            Dictionary with security group IDs
        """
        try:
            # Master security group
            master_sg_response = self.ec2_client.create_security_group(
                GroupName=f"{cluster_name}-master-sg",
                Description=f"Security group for {cluster_name} EMR master node",
                VpcId=vpc_id,
            )
            master_sg_id = master_sg_response["GroupId"]

            # Worker security group
            worker_sg_response = self.ec2_client.create_security_group(
                GroupName=f"{cluster_name}-worker-sg",
                Description=f"Security group for {cluster_name} EMR worker nodes",
                VpcId=vpc_id,
            )
            worker_sg_id = worker_sg_response["GroupId"]

            # Service access security group
            service_sg_response = self.ec2_client.create_security_group(
                GroupName=f"{cluster_name}-service-sg",
                Description=f"Security group for {cluster_name} EMR service access",
                VpcId=vpc_id,
            )
            service_sg_id = service_sg_response["GroupId"]

            # Configure security group rules
            self._configure_security_group_rules(
                master_sg_id, worker_sg_id, service_sg_id
            )

            # Tag security groups
            self.ec2_client.create_tags(
                Resources=[master_sg_id, worker_sg_id, service_sg_id],
                Tags=[
                    {"Key": "Name", "Value": f"{cluster_name}-emr-sg"},
                    {"Key": "EMRCluster", "Value": cluster_name},
                    {"Key": "Environment", "Value": "production"},
                    {"Key": "CreatedBy", "Value": "EMRClusterCreator"},
                ],
            )

            logger.info(
                f"Created security groups: Master={master_sg_id}, Worker={worker_sg_id}, Service={service_sg_id}"
            )

            return {
                "master": master_sg_id,
                "worker": worker_sg_id,
                "service": service_sg_id,
            }

        except ClientError as e:
            logger.error(f"Error creating security groups: {str(e)}")
            raise

    def _configure_security_group_rules(
        self, master_sg_id: str, worker_sg_id: str, service_sg_id: str
    ):
        """Configure security group rules for EMR cluster"""
        try:
            # Master node rules
            self.ec2_client.authorize_security_group_ingress(
                GroupId=master_sg_id,
                IpPermissions=[
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 22,
                        "ToPort": 22,
                        "IpRanges": [
                            {"CidrIp": "0.0.0.0/0", "Description": "SSH access"}
                        ],
                    },
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 8443,
                        "ToPort": 8443,
                        "UserIdGroupPairs": [
                            {
                                "GroupId": service_sg_id,
                                "Description": "EMR service access",
                            }
                        ],
                    },
                ],
            )

            # Worker node rules
            self.ec2_client.authorize_security_group_ingress(
                GroupId=worker_sg_id,
                IpPermissions=[
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 8443,
                        "ToPort": 8443,
                        "UserIdGroupPairs": [
                            {
                                "GroupId": service_sg_id,
                                "Description": "EMR service access",
                            }
                        ],
                    }
                ],
            )

            # Service access rules
            self.ec2_client.authorize_security_group_egress(
                GroupId=service_sg_id,
                IpPermissions=[
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 8443,
                        "ToPort": 8443,
                        "UserIdGroupPairs": [
                            {
                                "GroupId": master_sg_id,
                                "Description": "Access to master",
                            },
                            {
                                "GroupId": worker_sg_id,
                                "Description": "Access to workers",
                            },
                        ],
                    },
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 443,
                        "ToPort": 443,
                        "IpRanges": [
                            {"CidrIp": "0.0.0.0/0", "Description": "HTTPS outbound"}
                        ],
                    },
                ],
            )

            logger.info("Configured security group rules")

        except ClientError as e:
            logger.error(f"Error configuring security group rules: {str(e)}")
            raise

    def create_iam_roles(self, cluster_name: str) -> Dict[str, str]:
        """
        Create IAM roles for EMR cluster

        Args:
            cluster_name: Name of the EMR cluster

        Returns:
            Dictionary with IAM role ARNs
        """
        try:
            # EMR Service Role
            service_role_name = f"{cluster_name}-EMR-ServiceRole"
            service_trust_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "elasticmapreduce.amazonaws.com"},
                        "Action": "sts:AssumeRole",
                    }
                ],
            }

            try:
                service_role_response = self.iam_client.create_role(
                    RoleName=service_role_name,
                    AssumeRolePolicyDocument=json.dumps(service_trust_policy),
                    Description=f"EMR Service Role for {cluster_name}",
                    Tags=[
                        {"Key": "EMRCluster", "Value": cluster_name},
                        {"Key": "Environment", "Value": "production"},
                    ],
                )
                service_role_arn = service_role_response["Role"]["Arn"]
            except ClientError as e:
                if e.response["Error"]["Code"] == "EntityAlreadyExists":
                    service_role_arn = self.iam_client.get_role(
                        RoleName=service_role_name
                    )["Role"]["Arn"]
                else:
                    raise

            # Attach managed policy to service role
            self.iam_client.attach_role_policy(
                RoleName=service_role_name,
                PolicyArn="arn:aws:iam::aws:policy/service-role/AmazonElasticMapReduceRole",
            )

            # EMR EC2 Instance Profile Role
            instance_role_name = f"{cluster_name}-EMR-EC2-InstanceProfile"
            ec2_trust_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "ec2.amazonaws.com"},
                        "Action": "sts:AssumeRole",
                    }
                ],
            }

            try:
                instance_role_response = self.iam_client.create_role(
                    RoleName=instance_role_name,
                    AssumeRolePolicyDocument=json.dumps(ec2_trust_policy),
                    Description=f"EMR EC2 Instance Profile Role for {cluster_name}",
                    Tags=[
                        {"Key": "EMRCluster", "Value": cluster_name},
                        {"Key": "Environment", "Value": "production"},
                    ],
                )
                instance_role_arn = instance_role_response["Role"]["Arn"]
            except ClientError as e:
                if e.response["Error"]["Code"] == "EntityAlreadyExists":
                    instance_role_arn = self.iam_client.get_role(
                        RoleName=instance_role_name
                    )["Role"]["Arn"]
                else:
                    raise

            # Attach managed policies to instance role
            managed_policies = [
                "arn:aws:iam::aws:policy/service-role/AmazonElasticMapReduceforEC2Role",
                "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy",
            ]

            for policy_arn in managed_policies:
                self.iam_client.attach_role_policy(
                    RoleName=instance_role_name, PolicyArn=policy_arn
                )

            # Create instance profile
            instance_profile_name = f"{cluster_name}-EMR-EC2-InstanceProfile"
            try:
                self.iam_client.create_instance_profile(
                    InstanceProfileName=instance_profile_name,
                    Tags=[
                        {"Key": "EMRCluster", "Value": cluster_name},
                        {"Key": "Environment", "Value": "production"},
                    ],
                )

                # Add role to instance profile
                self.iam_client.add_role_to_instance_profile(
                    InstanceProfileName=instance_profile_name,
                    RoleName=instance_role_name,
                )
            except ClientError as e:
                if e.response["Error"]["Code"] != "EntityAlreadyExists":
                    raise

            # Auto Scaling Role (for managed scaling)
            autoscaling_role_name = f"{cluster_name}-EMR-AutoScaling-Role"
            autoscaling_trust_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": [
                                "elasticmapreduce.amazonaws.com",
                                "application-autoscaling.amazonaws.com",
                            ]
                        },
                        "Action": "sts:AssumeRole",
                    }
                ],
            }

            try:
                autoscaling_role_response = self.iam_client.create_role(
                    RoleName=autoscaling_role_name,
                    AssumeRolePolicyDocument=json.dumps(autoscaling_trust_policy),
                    Description=f"EMR Auto Scaling Role for {cluster_name}",
                    Tags=[
                        {"Key": "EMRCluster", "Value": cluster_name},
                        {"Key": "Environment", "Value": "production"},
                    ],
                )
                autoscaling_role_arn = autoscaling_role_response["Role"]["Arn"]
            except ClientError as e:
                if e.response["Error"]["Code"] == "EntityAlreadyExists":
                    autoscaling_role_arn = self.iam_client.get_role(
                        RoleName=autoscaling_role_name
                    )["Role"]["Arn"]
                else:
                    raise

            # Attach managed policy to auto scaling role
            self.iam_client.attach_role_policy(
                RoleName=autoscaling_role_name,
                PolicyArn="arn:aws:iam::aws:policy/service-role/AmazonElasticMapReduceforAutoScalingRole",
            )

            logger.info(
                f"Created IAM roles: Service={service_role_arn}, Instance={instance_role_arn}, AutoScaling={autoscaling_role_arn}"
            )

            # Wait for roles to be available
            time.sleep(10)

            return {
                "service_role": service_role_arn,
                "instance_profile": instance_profile_name,
                "autoscaling_role": autoscaling_role_arn,
            }

        except ClientError as e:
            logger.error(f"Error creating IAM roles: {str(e)}")
            raise

    def create_s3_bucket_for_logs(self, bucket_name: str) -> str:
        """
        Create S3 bucket for EMR logs

        Args:
            bucket_name: Name of the S3 bucket

        Returns:
            S3 bucket URI
        """
        try:
            # Check if bucket exists
            try:
                self.s3_client.head_bucket(Bucket=bucket_name)
                logger.info(f"S3 bucket {bucket_name} already exists")
            except ClientError as e:
                if e.response["Error"]["Code"] == "404":
                    # Create bucket
                    if self.region == "us-east-1":
                        self.s3_client.create_bucket(Bucket=bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=bucket_name,
                            CreateBucketConfiguration={
                                "LocationConstraint": self.region
                            },
                        )

                    # Enable versioning
                    self.s3_client.put_bucket_versioning(
                        Bucket=bucket_name,
                        VersioningConfiguration={"Status": "Enabled"},
                    )

                    # Enable server-side encryption
                    self.s3_client.put_bucket_encryption(
                        Bucket=bucket_name,
                        ServerSideEncryptionConfiguration={
                            "Rules": [
                                {
                                    "ApplyServerSideEncryptionByDefault": {
                                        "SSEAlgorithm": "AES256"
                                    }
                                }
                            ]
                        },
                    )

                    # Block public access
                    self.s3_client.put_public_access_block(
                        Bucket=bucket_name,
                        PublicAccessBlockConfiguration={
                            "BlockPublicAcls": True,
                            "IgnorePublicAcls": True,
                            "BlockPublicPolicy": True,
                            "RestrictPublicBuckets": True,
                        },
                    )

                    logger.info(f"Created S3 bucket: {bucket_name}")
                else:
                    raise

            return f"s3://{bucket_name}/"

        except ClientError as e:
            logger.error(f"Error creating S3 bucket: {str(e)}")
            raise

    def get_latest_emr_release(self) -> str:
        """Get the latest EMR release version"""
        try:
            response = self.emr_client.list_release_labels(MaxResults=1)
            latest_release = response["ReleaseLabels"][0]
            logger.info(f"Latest EMR release: {latest_release}")
            return latest_release
        except ClientError as e:
            logger.error(f"Error getting EMR releases: {str(e)}")
            return "emr-6.15.0"  # Fallback to known stable version

    def create_emr_cluster(self, config: Dict[str, Any]) -> str:
        """
        Create EMR cluster with comprehensive configuration

        Args:
            config: Cluster configuration dictionary

        Returns:
            Cluster ID
        """
        try:
            # Prepare cluster configuration
            cluster_config = {
                "Name": config["cluster_name"],
                "ReleaseLabel": config.get(
                    "release_label", self.get_latest_emr_release()
                ),
                "Applications": config.get(
                    "applications",
                    [
                        {"Name": "Spark"},
                        {"Name": "Hadoop"},
                        {"Name": "Hive"},
                        {"Name": "Pig"},
                        {"Name": "Zeppelin"},
                        {"Name": "JupyterHub"},
                        {"Name": "Livy"},
                    ],
                ),
                "Configurations": config.get(
                    "configurations",
                    [
                        {
                            "Classification": "spark-defaults",
                            "Properties": {
                                "spark.sql.adaptive.enabled": "true",
                                "spark.sql.adaptive.coalescePartitions.enabled": "true",
                                "spark.sql.adaptive.skewJoin.enabled": "true",
                                "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
                                "spark.sql.hive.metastorePartitionPruning": "true",
                            },
                        },
                        {
                            "Classification": "spark-env",
                            "Configurations": [
                                {
                                    "Classification": "export",
                                    "Properties": {
                                        "PYSPARK_PYTHON": "/usr/bin/python3"
                                    },
                                }
                            ],
                        },
                        {
                            "Classification": "hadoop-env",
                            "Configurations": [
                                {
                                    "Classification": "export",
                                    "Properties": {
                                        "HADOOP_DATANODE_HEAPSIZE": "2048",
                                        "HADOOP_NAMENODE_HEAPSIZE": "2048",
                                    },
                                }
                            ],
                        },
                    ],
                ),
                "ServiceRole": config["service_role"],
                "JobFlowRole": config["instance_profile"],
                "LogUri": config.get("log_uri"),
                "VisibleToAllUsers": config.get("visible_to_all_users", True),
                "Tags": config.get(
                    "tags",
                    [
                        {"Key": "Environment", "Value": "production"},
                        {"Key": "Project", "Value": config["cluster_name"]},
                        {"Key": "CreatedBy", "Value": "EMRClusterCreator"},
                        {"Key": "CreatedAt", "Value": datetime.now().isoformat()},
                    ],
                ),
            }

            # Instance groups configuration
            instance_groups = []

            # Master instance group
            master_config = config.get("master_instance", {})
            master_group = {
                "Name": "Master",
                "Market": master_config.get("market", "ON_DEMAND"),
                "InstanceRole": "MASTER",
                "InstanceType": master_config.get("instance_type", "m5.xlarge"),
                "InstanceCount": 1,
            }

            if master_config.get("market") == "SPOT":
                master_group["BidPrice"] = master_config.get("bid_price", "0.10")

            if master_config.get("ebs_config"):
                master_group["EbsConfiguration"] = master_config["ebs_config"]

            instance_groups.append(master_group)

            # Core instance group
            core_config = config.get("core_instances", {})
            if core_config.get("instance_count", 0) > 0:
                core_group = {
                    "Name": "Core",
                    "Market": core_config.get("market", "ON_DEMAND"),
                    "InstanceRole": "CORE",
                    "InstanceType": core_config.get("instance_type", "m5.large"),
                    "InstanceCount": core_config.get("instance_count", 2),
                }

                if core_config.get("market") == "SPOT":
                    core_group["BidPrice"] = core_config.get("bid_price", "0.05")

                if core_config.get("ebs_config"):
                    core_group["EbsConfiguration"] = core_config["ebs_config"]

                # Auto scaling configuration
                if core_config.get("auto_scaling"):
                    core_group["AutoScalingPolicy"] = {
                        "Constraints": {
                            "MinCapacity": core_config["auto_scaling"].get(
                                "min_capacity", 1
                            ),
                            "MaxCapacity": core_config["auto_scaling"].get(
                                "max_capacity", 10
                            ),
                        },
                        "Rules": core_config["auto_scaling"].get(
                            "rules",
                            [
                                {
                                    "Name": "ScaleOutMemoryPercentage",
                                    "Description": "Scale out if YARNMemoryAvailablePercentage is less than 15",
                                    "Action": {
                                        "Market": "ON_DEMAND",
                                        "SimpleScalingPolicyConfiguration": {
                                            "AdjustmentType": "CHANGE_IN_CAPACITY",
                                            "ScalingAdjustment": 1,
                                            "CoolDown": 300,
                                        },
                                    },
                                    "Trigger": {
                                        "CloudWatchAlarmDefinition": {
                                            "ComparisonOperator": "LESS_THAN",
                                            "EvaluationPeriods": 1,
                                            "MetricName": "YARNMemoryAvailablePercentage",
                                            "Namespace": "AWS/ElasticMapReduce",
                                            "Period": 300,
                                            "Statistic": "AVERAGE",
                                            "Threshold": 15.0,
                                            "Unit": "PERCENT",
                                        }
                                    },
                                }
                            ],
                        ),
                    }

                instance_groups.append(core_group)

            # Task instance group
            task_config = config.get("task_instances", {})
            if task_config.get("instance_count", 0) > 0:
                task_group = {
                    "Name": "Task",
                    "Market": task_config.get("market", "SPOT"),
                    "InstanceRole": "TASK",
                    "InstanceType": task_config.get("instance_type", "m5.large"),
                    "InstanceCount": task_config.get("instance_count", 0),
                }

                if task_config.get("market") == "SPOT":
                    task_group["BidPrice"] = task_config.get("bid_price", "0.05")

                if task_config.get("ebs_config"):
                    task_group["EbsConfiguration"] = task_config["ebs_config"]

                instance_groups.append(task_group)

            cluster_config["Instances"] = {
                "InstanceGroups": instance_groups,
                "Ec2KeyName": config.get("ec2_key_name"),
                "KeepJobFlowAliveWhenNoSteps": config.get("keep_alive", True),
                "TerminationProtected": config.get("termination_protected", False),
                "Ec2SubnetId": config.get("subnet_id"),
                "EmrManagedMasterSecurityGroup": config.get("master_security_group"),
                "EmrManagedSlaveSecurityGroup": config.get("worker_security_group"),
                "ServiceAccessSecurityGroup": config.get("service_security_group"),
                "AdditionalMasterSecurityGroups": config.get(
                    "additional_master_security_groups", []
                ),
                "AdditionalSlaveSecurityGroups": config.get(
                    "additional_worker_security_groups", []
                ),
            }

            # Bootstrap actions
            if config.get("bootstrap_actions"):
                cluster_config["BootstrapActions"] = config["bootstrap_actions"]

            # Steps
            if config.get("steps"):
                cluster_config["Steps"] = config["steps"]

            # Security configuration
            if config.get("security_configuration"):
                cluster_config["SecurityConfiguration"] = config[
                    "security_configuration"
                ]

            # Custom AMI
            if config.get("custom_ami_id"):
                cluster_config["CustomAmiId"] = config["custom_ami_id"]

            # EBS root volume size
            if config.get("ebs_root_volume_size"):
                cluster_config["EbsRootVolumeSize"] = config["ebs_root_volume_size"]

            # Repo upgrade on boot
            if config.get("repo_upgrade_on_boot"):
                cluster_config["RepoUpgradeOnBoot"] = config["repo_upgrade_on_boot"]

            # Kerberos attributes
            if config.get("kerberos_attributes"):
                cluster_config["KerberosAttributes"] = config["kerberos_attributes"]

            # Step concurrency level
            if config.get("step_concurrency_level"):
                cluster_config["StepConcurrencyLevel"] = config[
                    "step_concurrency_level"
                ]

            # Managed scaling policy
            if config.get("managed_scaling_policy"):
                cluster_config["ManagedScalingPolicy"] = config[
                    "managed_scaling_policy"
                ]

            # Auto scaling role
            if config.get("autoscaling_role"):
                cluster_config["AutoScalingRole"] = config["autoscaling_role"]

            # Scale down behavior
            if config.get("scale_down_behavior"):
                cluster_config["ScaleDownBehavior"] = config["scale_down_behavior"]

            # Auto termination policy
            if config.get("auto_termination_policy"):
                cluster_config["AutoTerminationPolicy"] = config[
                    "auto_termination_policy"
                ]

            logger.info(
                f"Creating EMR cluster with configuration: {json.dumps(cluster_config, indent=2, default=str)}"
            )

            # Create the cluster
            response = self.emr_client.run_job_flow(**cluster_config)
            cluster_id = response["JobFlowId"]

            logger.info(f"EMR cluster created successfully. Cluster ID: {cluster_id}")

            return cluster_id

        except ClientError as e:
            logger.error(f"Error creating EMR cluster: {str(e)}")
            raise

    def wait_for_cluster_ready(self, cluster_id: str, timeout: int = 1800) -> bool:
        """
        Wait for cluster to be in WAITING state

        Args:
            cluster_id: EMR cluster ID
            timeout: Timeout in seconds (default 30 minutes)

        Returns:
            True if cluster is ready, False if timeout or error
        """
        try:
            start_time = time.time()

            while time.time() - start_time < timeout:
                response = self.emr_client.describe_cluster(ClusterId=cluster_id)
                state = response["Cluster"]["Status"]["State"]

                logger.info(f"Cluster {cluster_id} state: {state}")

                if state == "WAITING":
                    logger.info(f"Cluster {cluster_id} is ready!")
                    return True
                elif state in ["TERMINATED", "TERMINATED_WITH_ERRORS", "TERMINATING"]:
                    logger.error(f"Cluster {cluster_id} terminated with state: {state}")
                    return False

                time.sleep(30)  # Wait 30 seconds before checking again

            logger.error(f"Timeout waiting for cluster {cluster_id} to be ready")
            return False

        except ClientError as e:
            logger.error(f"Error waiting for cluster: {str(e)}")
            return False

    def get_cluster_info(self, cluster_id: str) -> Dict[str, Any]:
        """
        Get comprehensive cluster information

        Args:
            cluster_id: EMR cluster ID

        Returns:
            Dictionary with cluster information
        """
        try:
            # Get cluster details
            cluster_response = self.emr_client.describe_cluster(ClusterId=cluster_id)
            cluster = cluster_response["Cluster"]

            # Get instance groups
            instance_groups_response = self.emr_client.list_instance_groups(
                ClusterId=cluster_id
            )
            instance_groups = instance_groups_response["InstanceGroups"]

            # Get instances
            instances_response = self.emr_client.list_instances(ClusterId=cluster_id)
            instances = instances_response["Instances"]

            cluster_info = {
                "cluster_id": cluster_id,
                "name": cluster["Name"],
                "state": cluster["Status"]["State"],
                "creation_time": cluster["Status"]["Timeline"]["CreationDateTime"],
                "master_public_dns": cluster.get("MasterPublicDnsName"),
                "release_label": cluster["ReleaseLabel"],
                "applications": [app["Name"] for app in cluster["Applications"]],
                "instance_groups": instance_groups,
                "instances": instances,
                "log_uri": cluster.get("LogUri"),
                "tags": cluster.get("Tags", []),
            }

            return cluster_info

        except ClientError as e:
            logger.error(f"Error getting cluster info: {str(e)}")
            raise

    def terminate_cluster(self, cluster_id: str) -> bool:
        """
        Terminate EMR cluster

        Args:
            cluster_id: EMR cluster ID

        Returns:
            True if termination initiated successfully
        """
        try:
            self.emr_client.terminate_job_flows(JobFlowIds=[cluster_id])
            logger.info(f"Cluster {cluster_id} termination initiated")
            return True

        except ClientError as e:
            logger.error(f"Error terminating cluster: {str(e)}")
            return False


def create_sample_configuration() -> Dict[str, Any]:
    """
    Create a sample configuration with all possible options

    Returns:
        Sample configuration dictionary
    """
    return {
        # Basic cluster settings
        "cluster_name": "my-emr-cluster",
        "release_label": "emr-6.15.0",  # Optional, will use latest if not specified

        # Applications to install
        "applications": [
            {"Name": "Spark"},
            {"Name": "Hadoop"},
            {"Name": "Hive"},
            {"Name": "Pig"},
            {"Name": "Zeppelin"},
            {"Name": "JupyterHub"},
            {"Name": "Livy"},
            {"Name": "Ganglia"},
            {"Name": "Presto"},
        ],

        # Configuration classifications
        "configurations": [
            {
                "Classification": "spark-defaults",
                "Properties": {
                    "spark.sql.adaptive.enabled": "true",
                    "spark.sql.adaptive.coalescePartitions.enabled": "true",
                    "spark.sql.adaptive.skewJoin.enabled": "true",
                    "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
                    "spark.sql.hive.metastorePartitionPruning": "true",
                    "spark.dynamicAllocation.enabled": "true",
                    "spark.dynamicAllocation.minExecutors": "1",
                    "spark.dynamicAllocation.maxExecutors": "10",
                },
            },
            {
                "Classification": "spark-env",
                "Configurations": [
                    {
                        "Classification": "export",
                        "Properties": {
                            "PYSPARK_PYTHON": "/usr/bin/python3",
                            "PYSPARK_DRIVER_PYTHON": "/usr/bin/python3",
                        },
                    }
                ],
            },
            {
                "Classification": "hadoop-env",
                "Configurations": [
                    {
                        "Classification": "export",
                        "Properties": {
                            "HADOOP_DATANODE_HEAPSIZE": "2048",
                            "HADOOP_NAMENODE_HEAPSIZE": "2048",
                        },
                    }
                ],
            },
            {
                "Classification": "yarn-site",
                "Properties": {
                    "yarn.nodemanager.vmem-check-enabled": "false",
                    "yarn.nodemanager.pmem-check-enabled": "false",
                },
            },
        ],

        # Master instance configuration
        "master_instance": {
            "instance_type": "m5.xlarge",
            "market": "ON_DEMAND",  # or 'SPOT'
            "bid_price": "0.10",  # Only for SPOT instances
            "ebs_config": {
                "EbsBlockDeviceConfigs": [
                    {
                        "VolumeSpecification": {
                            "SizeInGB": 100,
                            "VolumeType": "gp3",
                            "Iops": 3000,
                            "Throughput": 125,
                        },
                        "VolumesPerInstance": 1,
                    }
                ],
                "EbsOptimized": True,
            },
        },

        # Core instances configuration
        "core_instances": {
            "instance_type": "m5.large",
            "instance_count": 2,
            "market": "ON_DEMAND",  # or 'SPOT'
            "bid_price": "0.05",  # Only for SPOT instances
            "ebs_config": {
                "EbsBlockDeviceConfigs": [
                    {
                        "VolumeSpecification": {
                            "SizeInGB": 100,
                            "VolumeType": "gp3",
                            "Iops": 3000,
                            "Throughput": 125,
                        },
                        "VolumesPerInstance": 2,
                    }
                ],
                "EbsOptimized": True,
            },
            "auto_scaling": {
                "min_capacity": 1,
                "max_capacity": 10,
                "rules": [
                    {
                        "Name": "ScaleOutMemoryPercentage",
                        "Description": "Scale out if YARNMemoryAvailablePercentage is less than 15",
                        "Action": {
                            "Market": "ON_DEMAND",
                            "SimpleScalingPolicyConfiguration": {
                                "AdjustmentType": "CHANGE_IN_CAPACITY",
                                "ScalingAdjustment": 1,
                                "CoolDown": 300,
                            },
                        },
                        "Trigger": {
                            "CloudWatchAlarmDefinition": {
                                "ComparisonOperator": "LESS_THAN",
                                "EvaluationPeriods": 1,
                                "MetricName": "YARNMemoryAvailablePercentage",
                                "Namespace": "AWS/ElasticMapReduce",
                                "Period": 300,
                                "Statistic": "AVERAGE",
                                "Threshold": 15.0,
                                "Unit": "PERCENT",
                            }
                        },
                    },
                    {
                        "Name": "ScaleInMemoryPercentage",
                        "Description": "Scale in if YARNMemoryAvailablePercentage is greater than 75",
                        "Action": {
                            "SimpleScalingPolicyConfiguration": {
                                "AdjustmentType": "CHANGE_IN_CAPACITY",
                                "ScalingAdjustment": -1,
                                "CoolDown": 300,
                            }
                        },
                        "Trigger": {
                            "CloudWatchAlarmDefinition": {
                                "ComparisonOperator": "GREATER_THAN",
                                "EvaluationPeriods": 1,
                                "MetricName": "YARNMemoryAvailablePercentage",
                                "Namespace": "AWS/ElasticMapReduce",
                                "Period": 300,
                                "Statistic": "AVERAGE",
                                "Threshold": 75.0,
                                "Unit": "PERCENT",
                            }
                        },
                    },
                ],
            },
        },

        # Task instances configuration (optional)
        "task_instances": {
            "instance_type": "m5.large",
            "instance_count": 0,  # Set to 0 to disable task instances
            "market": "SPOT",
            "bid_price": "0.05",
            "ebs_config": {
                "EbsBlockDeviceConfigs": [
                    {
                        "VolumeSpecification": {"SizeInGB": 50, "VolumeType": "gp3"},
                        "VolumesPerInstance": 1,
                    }
                ],
                "EbsOptimized": True,
            },
        },

        # Network configuration
        "vpc_id": None,  # Will be detected automatically if not provided
        "subnet_id": None,  # Will use default subnet if not provided
        "ec2_key_name": None,  # SSH key pair name (optional)

        # Security groups (will be created if not provided)
        "master_security_group": None,
        "worker_security_group": None,
        "service_security_group": None,
        "additional_master_security_groups": [],
        "additional_worker_security_groups": [],

        # IAM roles (will be created if not provided)
        "service_role": None,
        "instance_profile": None,
        "autoscaling_role": None,

        # Logging configuration
        "log_uri": None,  # S3 URI for logs (will be created if not provided)
        "log_bucket_name": None,  # S3 bucket name for logs

        # Cluster behavior
        "keep_alive": True,  # Keep cluster alive when no steps
        "termination_protected": False,  # Protect against accidental termination
        "visible_to_all_users": True,  # Visible to all IAM users

        # Bootstrap actions (optional)
        "bootstrap_actions": [
            {
                "Name": "Install Additional Packages",
                "ScriptBootstrapAction": {
                    "Path": "s3://your-bucket/bootstrap-scripts/install-packages.sh",
                    "Args": ["--packages", "pandas,numpy,scikit-learn"],
                },
            }
        ],

        # Steps to run (optional)
        "steps": [
            {
                "Name": "Setup Hadoop Debugging",
                "ActionOnFailure": "TERMINATE_CLUSTER",
                "HadoopJarStep": {
                    "Jar": "command-runner.jar",
                    "Args": ["state-pusher-script"],
                },
            }
        ],

        # Advanced configurations
        "security_configuration": None,  # Security configuration name
        "custom_ami_id": None,  # Custom AMI ID
        "ebs_root_volume_size": 20,  # Root volume size in GB
        "repo_upgrade_on_boot": "SECURITY",  # SECURITY, NONE, or ALL
        "step_concurrency_level": 1,  # Number of steps that can run concurrently
        "scale_down_behavior": "TERMINATE_AT_TASK_COMPLETION",  # or 'TERMINATE_AT_INSTANCE_HOUR'

        # Managed scaling policy (alternative to auto scaling)
        "managed_scaling_policy": {
            "ComputeLimits": {
                "UnitType": "Instances",  # or 'VCPU'
                "MinimumCapacityUnits": 1,
                "MaximumCapacityUnits": 10,
                "MaximumOnDemandCapacityUnits": 5,
                "MaximumCoreCapacityUnits": 5,
            }
        },

        # Auto termination policy
        "auto_termination_policy": {
            "IdleTimeout": 3600  # Terminate after 1 hour of inactivity
        },

        # Kerberos configuration (optional)
        "kerberos_attributes": {
            "Realm": "EC2.INTERNAL",
            "KdcAdminPassword": "YourKerberosPassword",
            "CrossRealmTrustPrincipalPassword": "YourCrossRealmPassword",
            "ADDomainJoinUser": "YourADUser",
            "ADDomainJoinPassword": "YourADPassword",
        },

        # Tags
        "tags": [
            {"Key": "Environment", "Value": "production"},
            {"Key": "Project", "Value": "data-analytics"},
            {"Key": "Owner", "Value": "data-team"},
            {"Key": "CostCenter", "Value": "12345"},
            {"Key": "CreatedBy", "Value": "EMRClusterCreator"},
            {"Key": "CreatedAt", "Value": datetime.now().isoformat()},
        ],
    }


def main():
    """
    Main function to create EMR cluster
    """
    # Get configuration from environment variables or use defaults
    aws_profile = os.getenv("AWS_PROFILE")
    aws_region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

    # Initialize EMR cluster creator
    emr_creator = EMRClusterCreator(aws_profile=aws_profile, region=aws_region)

    # Create sample configuration
    config = create_sample_configuration()

    # Customize configuration based on environment variables
    config["cluster_name"] = os.getenv("EMR_CLUSTER_NAME", config["cluster_name"])
    config["ec2_key_name"] = os.getenv("EC2_KEY_NAME", config["ec2_key_name"])
    config["subnet_id"] = os.getenv("SUBNET_ID", config["subnet_id"])
    config["vpc_id"] = os.getenv("VPC_ID", config["vpc_id"])

    try:
        # Get default VPC if not specified
        if not config["vpc_id"]:
            vpcs = emr_creator.ec2_client.describe_vpcs(
                Filters=[{"Name": "is-default", "Values": ["true"]}]
            )
            if vpcs["Vpcs"]:
                config["vpc_id"] = vpcs["Vpcs"][0]["VpcId"]
                logger.info(f"Using default VPC: {config['vpc_id']}")

        # Get default subnet if not specified
        if not config["subnet_id"] and config["vpc_id"]:
            subnets = emr_creator.ec2_client.describe_subnets(
                Filters=[
                    {"Name": "vpc-id", "Values": [config["vpc_id"]]},
                    {"Name": "default-for-az", "Values": ["true"]},
                ]
            )
            if subnets["Subnets"]:
                config["subnet_id"] = subnets["Subnets"][0]["SubnetId"]
                logger.info(f"Using default subnet: {config['subnet_id']}")

        # Create S3 bucket for logs if not specified
        if not config["log_uri"]:
            bucket_name = (
                config.get("log_bucket_name")
                or f"{config['cluster_name']}-logs-{int(time.time())}"
            )
            config["log_uri"] = emr_creator.create_s3_bucket_for_logs(bucket_name)

        # Create IAM roles if not specified
        if not config["service_role"] or not config["instance_profile"]:
            iam_roles = emr_creator.create_iam_roles(config["cluster_name"])
            config["service_role"] = config["service_role"] or iam_roles["service_role"]
            config["instance_profile"] = (
                config["instance_profile"] or iam_roles["instance_profile"]
            )
            config["autoscaling_role"] = (
                config["autoscaling_role"] or iam_roles["autoscaling_role"]
            )

        # Create security groups if not specified
        if not config["master_security_group"] or not config["worker_security_group"]:
            security_groups = emr_creator.create_security_groups(
                config["vpc_id"], config["cluster_name"]
            )
            config["master_security_group"] = (
                config["master_security_group"] or security_groups["master"]
            )
            config["worker_security_group"] = (
                config["worker_security_group"] or security_groups["worker"]
            )
            config["service_security_group"] = (
                config["service_security_group"] or security_groups["service"]
            )

        # Create EMR cluster
        cluster_id = emr_creator.create_emr_cluster(config)

        print(f"\n{'=' * 60}")
        print(f"EMR CLUSTER CREATED SUCCESSFULLY")
        print(f"{'=' * 60}")
        print(f"Cluster ID: {cluster_id}")
        print(f"Cluster Name: {config['cluster_name']}")
        print(f"Region: {aws_region}")
        print(f"Log URI: {config['log_uri']}")
        print(f"{'=' * 60}")

        # Wait for cluster to be ready (optional)
        wait_for_ready = os.getenv("WAIT_FOR_CLUSTER_READY", "false").lower() == "true"
        if wait_for_ready:
            print("\nWaiting for cluster to be ready...")
            if emr_creator.wait_for_cluster_ready(cluster_id):
                cluster_info = emr_creator.get_cluster_info(cluster_id)
                print(f"\nCluster is ready!")
                print(
                    f"Master Public DNS: {cluster_info.get('master_public_dns', 'N/A')}"
                )
                print(f"State: {cluster_info['state']}")
            else:
                print("\nCluster failed to start or timed out")

        return cluster_id

    except Exception as e:
        logger.error(f"Failed to create EMR cluster: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
