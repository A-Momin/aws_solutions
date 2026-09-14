import os
import json
import time
import yaml
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import boto3
from botocore.exceptions import ClientError

from mylogger import CustomLogger
logger = CustomLogger()

@dataclass
class NetworkConfig:
    """Network configuration for Redshift cluster"""

    vpc_cidr: str = "10.0.0.0/16"
    subnet_cidrs: List[str] = None
    availability_zones: List[str] = None
    enable_dns_hostnames: bool = True
    enable_dns_support: bool = True

    def __post_init__(self):
        if self.subnet_cidrs is None:
            self.subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24"]
        if self.availability_zones is None:
            self.availability_zones = []


@dataclass
class SecurityConfig:
    """Security configuration for Redshift cluster"""

    allowed_cidr_blocks: List[str] = None
    allowed_security_group_ids: List[str] = None
    port: int = 5439

    def __post_init__(self):
        if self.allowed_cidr_blocks is None:
            self.allowed_cidr_blocks = ["0.0.0.0/0"]  # Warning: Very permissive
        if self.allowed_security_group_ids is None:
            self.allowed_security_group_ids = []


@dataclass
class RedshiftClusterConfig:
    """Comprehensive Redshift cluster configuration"""

    # Required parameters
    cluster_identifier: str
    master_username: str
    master_password: str
    node_type: str = "ra3.xlplus" # dc2.large, ra3.xlplus

    # Optional basic parameters
    database_name: str = "dev-rs-db"
    number_of_nodes: int = 1
    cluster_type: str = "single-node"  # single-node or multi-node
    port: int = 5439

    # Advanced configuration
    cluster_version: str = "1.0"
    allow_version_upgrade: bool = True
    auto_minor_version_upgrade: bool = True

    # Security and networking
    publicly_accessible: bool = False
    encrypted: bool = True
    kms_key_id: Optional[str] = None
    enhanced_vpc_routing: bool = False

    # Backup and maintenance
    automated_snapshot_retention_period: int = 7
    preferred_maintenance_window: Optional[str] = None  # "sun:05:00-sun:06:00"
    skip_final_snapshot: bool = False
    final_snapshot_identifier: Optional[str] = None

    # Monitoring and logging
    enable_logging: bool = True
    bucket_name: Optional[str] = None
    s3_key_prefix: Optional[str] = None
    enable_user_activity_logging: bool = False

    # Performance
    cluster_parameter_group_name: Optional[str] = None
    cluster_security_groups: List[str] = None
    vpc_security_group_ids: List[str] = None

    # Advanced features
    elastic_ip: Optional[str] = None
    hsm_client_certificate_identifier: Optional[str] = None
    hsm_configuration_identifier: Optional[str] = None

    # Snapshot settings
    manual_snapshot_retention_period: int = -1
    snapshot_copy_retention_period: int = -1
    snapshot_copy_destination_region: Optional[str] = None
    snapshot_copy_grant_name: Optional[str] = None

    # Tags
    tags: Dict[str, str] = None

    def __post_init__(self):
        if self.cluster_security_groups is None:
            self.cluster_security_groups = []
        if self.vpc_security_group_ids is None:
            self.vpc_security_group_ids = []
        if self.tags is None:
            self.tags = {}
        if self.cluster_type == "single-node":
            self.number_of_nodes = 1


class RedshiftClusterManager:
    """Manages AWS Redshift cluster creation and all dependent resources"""

    def __init__(self, region_name: str = None, profile_name: str = None):
        """
        Initialize the Redshift Cluster Manager

        Args:
            region_name: AWS region (defaults to environment variable or us-east-1)
            profile_name: AWS profile name (defaults to environment variable)
        """
        self.region_name = region_name or os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.profile_name = profile_name or os.getenv("AWS_PROFILE")

        # Initialize AWS session
        session_kwargs = {"region_name": self.region_name}
        if self.profile_name:
            session_kwargs["profile_name"] = self.profile_name

        self.session = boto3.Session(**session_kwargs)

        # Initialize AWS clients
        self.ec2_client = self.session.client("ec2")
        self.redshift_client = self.session.client("redshift")
        self.iam_client = self.session.client("iam")
        self.s3_client = self.session.client("s3")

        # Storage for created resources
        self.created_resources = {}

        logger.info(f"Initialized RedshiftClusterManager for region: {self.region_name}")

    def create_vpc_infrastructure(self, 
            network_config: NetworkConfig, 
            resource_prefix: str = "redshift"
        ) -> Dict[str, str]:
        """
        Create VPC infrastructure for Redshift cluster

        Args:
            network_config: Network configuration
            resource_prefix: Prefix for resource names

        Returns:
            Dict containing VPC infrastructure resource IDs
        """
        try:
            logger.info("Creating VPC infrastructure...")

            # Create VPC
            vpc_response = self.ec2_client.create_vpc(
                CidrBlock=network_config.vpc_cidr,
                # EnableDnsHostnames=network_config.enable_dns_hostnames,
                # EnableDnsSupport=network_config.enable_dns_support,
            )
            vpc_id = vpc_response["Vpc"]["VpcId"]

            # Tag VPC
            self.ec2_client.create_tags(
                Resources=[vpc_id],
                Tags=[{"Key": "Name", "Value": f"{resource_prefix}-vpc"}],
            )

            # Create Internet Gateway
            igw_response = self.ec2_client.create_internet_gateway()
            igw_id = igw_response["InternetGateway"]["InternetGatewayId"]

            # Attach Internet Gateway to VPC
            self.ec2_client.attach_internet_gateway(
                InternetGatewayId=igw_id, VpcId=vpc_id
            )

            # Tag Internet Gateway
            self.ec2_client.create_tags(
                Resources=[igw_id],
                Tags=[{"Key": "Name", "Value": f"{resource_prefix}-igw"}],
            )

            # Get availability zones
            if not network_config.availability_zones:
                azs_response = self.ec2_client.describe_availability_zones()
                network_config.availability_zones = [
                    az["ZoneName"] for az in azs_response["AvailabilityZones"][:2]
                ]

            # Create subnets
            subnet_ids = []
            for i, (cidr, az) in enumerate(zip(network_config.subnet_cidrs, network_config.availability_zones)):
                subnet_response = self.ec2_client.create_subnet(
                    VpcId=vpc_id, CidrBlock=cidr, AvailabilityZone=az
                )
                subnet_id = subnet_response["Subnet"]["SubnetId"]
                subnet_ids.append(subnet_id)

                # Tag subnet
                self.ec2_client.create_tags(
                    Resources=[subnet_id],
                    Tags=[
                        {"Key": "Name", "Value": f"{resource_prefix}-subnet-{i + 1}"}
                    ],
                )

            # Create route table
            route_table_response = self.ec2_client.create_route_table(VpcId=vpc_id)
            route_table_id = route_table_response["RouteTable"]["RouteTableId"]

            # Add route to Internet Gateway
            self.ec2_client.create_route(
                RouteTableId=route_table_id,
                DestinationCidrBlock="0.0.0.0/0",
                GatewayId=igw_id,
            )

            # Associate subnets with route table
            for subnet_id in subnet_ids:
                self.ec2_client.associate_route_table(
                    RouteTableId=route_table_id, SubnetId=subnet_id
                )

            # Tag route table
            self.ec2_client.create_tags(
                Resources=[route_table_id],
                Tags=[{"Key": "Name", "Value": f"{resource_prefix}-rt"}],
            )


            # Create an VPC (Gateway Interface) Endpoint
            vpc_endpoint_id = self.ec2_client.create_vpc_endpoint(
                VpcEndpointType="Gateway",
                VpcId=vpc_id,
                ServiceName="com.amazonaws.us-east-1.s3",
                RouteTableIds=[route_table_id],
                PrivateDnsEnabled=False,  # Enable private DNS to resolve service names within the VPC
            )["VpcEndpoint"]["VpcEndpointId"]

            vpc_infrastructure = {
                "vpc_id": vpc_id,
                "internet_gateway_id": igw_id,
                "subnet_ids": subnet_ids,
                "route_table_id": route_table_id,
                "vpc_endpoint_id": vpc_endpoint_id
            }

            self.created_resources.update(vpc_infrastructure)
            logger.info(
                f"VPC infrastructure created successfully: {vpc_infrastructure}"
            )

            return vpc_infrastructure

        except ClientError as e:
            logger.error(f"Failed to create VPC infrastructure: {e}")
            raise

    def create_security_group(self,vpc_id: str,security_config: SecurityConfig,resource_prefix: str = "redshift") -> str:
        """
        Create security group for Redshift cluster

        Args:
            vpc_id: VPC ID where security group will be created
            security_config: Security configuration
            resource_prefix: Prefix for resource names

        Returns:
            Security group ID
        """
        try:
            logger.info("Creating security group...")

            # Create security group
            sg_response = self.ec2_client.create_security_group(
                GroupName=f"{resource_prefix}-sg",
                Description=f"Security group for {resource_prefix} Redshift cluster",
                VpcId=vpc_id,
            )
            security_group_id = sg_response["GroupId"]

            # Add inbound rules
            ingress_rules = []

            # Add rules for CIDR blocks
            for cidr in security_config.allowed_cidr_blocks:
                ingress_rules.append(
                    {
                        "IpProtocol": "tcp",
                        "FromPort": security_config.port,
                        "ToPort": security_config.port,
                        "IpRanges": [{"CidrIp": cidr}],
                    }
                )

            # One of the security groups that's associated with the connection must have a self-referenced inbound rule that's open to all TCP ports. One of the security groups must be open to all outbound traffic.
            ingress_rules.append(
                {
                    "IpProtocol": "tcp",
                    "FromPort": 0,
                    "ToPort": 65535,
                    "UserIdGroupPairs": [
                        {
                            "GroupId": security_group_id,  # Same as the security group it's attached to
                        }
                    ],
                }
            )

            # Add rules for security groups
            for sg_id in security_config.allowed_security_group_ids:
                ingress_rules.append(
                    {
                        "IpProtocol": "tcp",
                        "FromPort": security_config.port,
                        "ToPort": security_config.port,
                        "UserIdGroupPairs": [
                            {
                                "GroupId": sg_id,
                            }
                        ],
                    }
                )

            if ingress_rules:
                self.ec2_client.authorize_security_group_ingress(
                    GroupId=security_group_id, IpPermissions=ingress_rules
                )

            # Tag security group
            self.ec2_client.create_tags(
                Resources=[security_group_id],
                Tags=[{"Key": "Name", "Value": f"{resource_prefix}-sg"}],
            )

            self.created_resources["security_group_id"] = security_group_id
            logger.info(f"Security group created: {security_group_id}")

            return security_group_id

        except ClientError as e:
            logger.error(f"Failed to create security group: {e}")
            raise

    def create_iam_role(self, role_name: str, resource_prefix: str = "redshift") -> str:
        """
        Create IAM role for Redshift cluster

        Args:
            role_name: Name for the IAM role
            resource_prefix: Prefix for resource names

        Returns:
            IAM role ARN
        """
        try:
            logger.info(f"Creating IAM role: {role_name}")

            # Trust policy for Redshift
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "redshift.amazonaws.com"},
                        "Action": "sts:AssumeRole",
                    }
                ],
            }

            # Create IAM role
            role_response = self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description=f"IAM role for {resource_prefix} Redshift cluster",
            )
            role_arn = role_response["Role"]["Arn"]

            # Attach common policies
            policies_to_attach = [
                "arn:aws:iam::aws:policy/AmazonRedshiftFullAccess",
                "arn:aws:iam::aws:policy/AmazonRedshiftQueryEditorV2FullAccess",
                "arn:aws:iam::aws:policy/AmazonS3FullAccess",
                "arn:aws:iam::aws:policy/AmazonAthenaFullAccess",
                "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole",
                "arn:aws:iam::aws:policy/AmazonRDSFullAccess",
                "arn:aws:iam::aws:policy/AdministratorAccess",
                "arn:aws:iam::aws:policy/PowerUserAccess",
            ]

            for policy_arn in policies_to_attach:
                try:
                    self.iam_client.attach_role_policy(
                        RoleName=role_name, PolicyArn=policy_arn
                    )
                except ClientError as e:
                    logger.warning(f"Could not attach policy {policy_arn}: {e}")

            # Wait for role to be available
            time.sleep(10)

            self.created_resources["iam_role_arn"] = role_arn
            logger.info(f"IAM role created: {role_arn}")

            return role_arn

        except ClientError as e:
            logger.error(f"Failed to create IAM role: {e}")
            raise

    def create_subnet_group(self,subnet_group_name: str,subnet_ids: List[str],resource_prefix: str = "redshift") -> str:
        """
        Create Redshift subnet group

        Args:
            subnet_group_name: Name for the subnet group
            subnet_ids: List of subnet IDs
            resource_prefix: Prefix for resource names

        Returns:
            Subnet group name
        """
        try:
            logger.info(f"Creating subnet group: {subnet_group_name}")

            self.redshift_client.create_cluster_subnet_group(
                ClusterSubnetGroupName=subnet_group_name,
                Description=f"Subnet group for {resource_prefix} Redshift cluster",
                SubnetIds=subnet_ids,
            )

            self.created_resources["subnet_group_name"] = subnet_group_name
            logger.info(f"Subnet group created: {subnet_group_name}")

            return subnet_group_name

        except ClientError as e:
            logger.error(f"Failed to create subnet group: {e}")
            raise

    def create_parameter_group(self,
            parameter_group_name: str,
            parameters: Dict[str, str] = None,
            family: str = "redshift-1.0"
        ) -> str:
        """
        Create Redshift parameter group

        Args:
            parameter_group_name: Name for the parameter group
            parameters: Dict of parameter names and values
            family: Parameter group family

        Returns:
            Parameter group name
        """
        try:
            logger.info(f"Creating parameter group: {parameter_group_name}")

            # Create parameter group
            self.redshift_client.create_cluster_parameter_group(
                ParameterGroupName=parameter_group_name,
                ParameterGroupFamily=family,
                Description=f"Parameter group for Redshift cluster",
            )

            # Set parameters if provided
            if parameters:
                parameter_list = [
                    {"ParameterName": name, "ParameterValue": value}
                    for name, value in parameters.items()
                ]

                self.redshift_client.modify_cluster_parameter_group(
                    ParameterGroupName=parameter_group_name, Parameters=parameter_list
                )

            self.created_resources["parameter_group_name"] = parameter_group_name
            logger.info(f"Parameter group created: {parameter_group_name}")

            return parameter_group_name

        except ClientError as e:
            logger.error(f"Failed to create parameter group: {e}")
            raise

    def create_redshift_cluster(self,
            cluster_config: RedshiftClusterConfig,
            subnet_group_name: str,
            vpc_security_group_ids: List[str],
            iam_role_arn: str = None
        ) -> Dict[str, Any]:
        """
        Create Redshift cluster with comprehensive configuration

        Args:
            cluster_config: Redshift cluster configuration
            subnet_group_name: Subnet group name
            vpc_security_group_ids: List of VPC security group IDs
            iam_role_arn: IAM role ARN (optional)

        Returns:
            Dict containing cluster information
        """
        try:
            logger.info(
                f"Creating Redshift cluster: {cluster_config.cluster_identifier}"
            )

            # Prepare cluster creation parameters
            create_params = {
                "ClusterIdentifier": cluster_config.cluster_identifier,
                "NodeType": cluster_config.node_type,
                "MasterUsername": cluster_config.master_username,
                "MasterUserPassword": cluster_config.master_password,
                "DBName": cluster_config.database_name,
                "Port": cluster_config.port,
                "ClusterVersion": cluster_config.cluster_version,
                "AllowVersionUpgrade": cluster_config.allow_version_upgrade,
                # "AutoMinorVersionUpgrade": cluster_config.auto_minor_version_upgrade,
                "PubliclyAccessible": cluster_config.publicly_accessible,
                "Encrypted": cluster_config.encrypted,
                "EnhancedVpcRouting": cluster_config.enhanced_vpc_routing,
                "AutomatedSnapshotRetentionPeriod": cluster_config.automated_snapshot_retention_period,
                "ManualSnapshotRetentionPeriod": cluster_config.manual_snapshot_retention_period,
                "ClusterSubnetGroupName": subnet_group_name,
                "VpcSecurityGroupIds": vpc_security_group_ids
                + cluster_config.vpc_security_group_ids,
            }

            # Add cluster type and number of nodes
            if cluster_config.cluster_type == "single-node":
                create_params["ClusterType"] = "single-node"
            else:
                create_params["ClusterType"] = "multi-node"
                create_params["NumberOfNodes"] = cluster_config.number_of_nodes

            # Add optional parameters
            if cluster_config.kms_key_id:
                create_params["KmsKeyId"] = cluster_config.kms_key_id

            if cluster_config.preferred_maintenance_window:
                create_params["PreferredMaintenanceWindow"] = (
                    cluster_config.preferred_maintenance_window
                )

            if cluster_config.cluster_parameter_group_name:
                create_params["ClusterParameterGroupName"] = (
                    cluster_config.cluster_parameter_group_name
                )

            if cluster_config.cluster_security_groups:
                create_params["ClusterSecurityGroups"] = (
                    cluster_config.cluster_security_groups
                )

            if cluster_config.elastic_ip:
                create_params["ElasticIp"] = cluster_config.elastic_ip

            if cluster_config.hsm_client_certificate_identifier:
                create_params["HsmClientCertificateIdentifier"] = (
                    cluster_config.hsm_client_certificate_identifier
                )

            if cluster_config.hsm_configuration_identifier:
                create_params["HsmConfigurationIdentifier"] = (
                    cluster_config.hsm_configuration_identifier
                )

            if iam_role_arn:
                create_params["IamRoles"] = [iam_role_arn]

            # Add tags
            if cluster_config.tags:
                create_params["Tags"] = [
                    {"Key": key, "Value": value}
                    for key, value in cluster_config.tags.items()
                ]

            # Logging configuration
            if cluster_config.enable_logging and cluster_config.bucket_name:
                logging_properties = {
                    "Enable": True,
                    "BucketName": cluster_config.bucket_name,
                }
                if cluster_config.s3_key_prefix:
                    logging_properties["S3KeyPrefix"] = cluster_config.s3_key_prefix

                create_params["LoggingProperties"] = logging_properties

            # Create the cluster
            response = self.redshift_client.create_cluster(**create_params)
            cluster_info = response["Cluster"]

            self.created_resources["cluster_identifier"] = (
                cluster_config.cluster_identifier
            )
            logger.info(
                f"Redshift cluster creation initiated: {cluster_config.cluster_identifier}"
            )

            return cluster_info

        except ClientError as e:
            logger.error(f"Failed to create Redshift cluster: {e}")
            raise

    def wait_for_cluster_available(self, cluster_identifier: str, max_wait_time: int = 1800) -> Dict[str, Any]:
        """
        Wait for Redshift cluster to become available

        Args:
            cluster_identifier: Cluster identifier
            max_wait_time: Maximum wait time in seconds (default: 30 minutes)

        Returns:
            Dict containing final cluster information
        """
        logger.info(f"Waiting for cluster {cluster_identifier} to become available...")

        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            try:
                response = self.redshift_client.describe_clusters(
                    ClusterIdentifier=cluster_identifier
                )
                cluster = response["Clusters"][0]
                status = cluster["ClusterStatus"]

                logger.info(f"Cluster status: {status}")

                if status == "available":
                    logger.info("Cluster is now available!")

                    endpoint = response['Clusters'][0]['Endpoint']['Address']
                    port = response['Clusters'][0]['Endpoint']['Port']
                    db_name = response['Clusters'][0]['DBName']
                    jdbc_url = f"jdbc:redshift://{endpoint}:{port}/{db_name}"

                    self.created_resources["jdbc_url"] = jdbc_url

                    return cluster
                elif status in ["creating", "modifying", "rebooting"]:
                    time.sleep(30)
                else:
                    raise Exception(f"Cluster entered unexpected state: {status}")

            except ClientError as e:
                logger.error(f"Error checking cluster status: {e}")
                time.sleep(30)

        raise Exception(
            f"Cluster did not become available within {max_wait_time} seconds"
        )

    def create_complete_redshift_environment(self,
            cluster_config: RedshiftClusterConfig,
            network_config: NetworkConfig = None,
            security_config: SecurityConfig = None,
            resource_prefix: str = "redshift",
            create_iam_role: bool = True,
            create_parameter_group: bool = False,
            parameter_group_parameters: Dict[str, str] = None,
            wait_for_available: bool = True,
        ) -> Dict[str, Any]:
        """
        Create complete Redshift environment with all dependencies

        Args:
            cluster_config: Redshift cluster configuration
            network_config: Network configuration (optional, defaults will be used)
            security_config: Security configuration (optional, defaults will be used)
            resource_prefix: Prefix for all resource names
            create_iam_role: Whether to create IAM role
            create_parameter_group: Whether to create parameter group
            parameter_group_parameters: Parameters for parameter group
            wait_for_available: Whether to wait for cluster to become available

        Returns:
            Dict containing all created resources and cluster information
        """
        try:
            logger.info("Starting complete Redshift environment creation...")

            # Use defaults if configs not provided
            if network_config is None:
                network_config = NetworkConfig()
            if security_config is None:
                security_config = SecurityConfig()

            # Create VPC infrastructure
            vpc_infrastructure = self.create_vpc_infrastructure(
                network_config, resource_prefix
            )

            # Create security group
            security_group_id = self.create_security_group(
                vpc_infrastructure["vpc_id"], security_config, resource_prefix
            )

            # Create subnet group
            subnet_group_name = f"{resource_prefix}-subnet-group"
            self.create_subnet_group(
                subnet_group_name, vpc_infrastructure["subnet_ids"], resource_prefix
            )

            # Create IAM role if requested
            iam_role_arn = None
            if create_iam_role:
                role_name = f"{resource_prefix}-role"
                iam_role_arn = self.create_iam_role(role_name, resource_prefix)

            # Create parameter group if requested
            if create_parameter_group:
                parameter_group_name = f"{resource_prefix}-params"
                cluster_config.cluster_parameter_group_name = (
                    self.create_parameter_group(
                        parameter_group_name, parameter_group_parameters
                    )
                )

            # Create Redshift cluster
            cluster_info = self.create_redshift_cluster(
                cluster_config, subnet_group_name, [security_group_id], iam_role_arn
            )

            # Wait for cluster to become available if requested
            if wait_for_available:
                cluster_info = self.wait_for_cluster_available(
                    cluster_config.cluster_identifier
                )

            # Compile results
            result = {
                "cluster_info": cluster_info,
                "vpc_infrastructure": vpc_infrastructure,
                "security_group_id": security_group_id,
                "subnet_group_name": subnet_group_name,
                "iam_role_arn": iam_role_arn,
                "created_resources": self.created_resources,
            }

            logger.info("Redshift environment creation completed successfully!")
            return result

        except Exception as e:
            logger.error(f"Failed to create Redshift environment: {e}")
            # In a production environment, you might want to implement cleanup here
            raise

    def cleanup_resources(
            self,
            cluster_identifier: str = None,
            skip_final_snapshot: bool = True,
            final_snapshot_identifier: str = None,
        ):
        """
        Cleanup created resources (use with caution!)

        Args:
            cluster_identifier: Cluster to delete (if None, uses stored value)
            skip_final_snapshot: Whether to skip final snapshot
            final_snapshot_identifier: Final snapshot identifier
        """
        logger.warning("Starting resource cleanup - this will delete resources!")

        try:
            # Delete cluster
            if cluster_identifier or "cluster_identifier" in self.created_resources:
                cluster_id = (
                    cluster_identifier or self.created_resources["cluster_identifier"]
                )
                delete_params = {
                    "ClusterIdentifier": cluster_id,
                    "SkipFinalClusterSnapshot": skip_final_snapshot,
                }
                if not skip_final_snapshot and final_snapshot_identifier:
                    delete_params["FinalClusterSnapshotIdentifier"] = (
                        final_snapshot_identifier
                    )

                self.redshift_client.delete_cluster(**delete_params)
                logger.info(f"Initiated cluster deletion: {cluster_id}")

            # Wait a bit for cluster deletion to start
            time.sleep(30)

            # Delete subnet group
            if "subnet_group_name" in self.created_resources:
                self.redshift_client.delete_cluster_subnet_group(
                    ClusterSubnetGroupName=self.created_resources["subnet_group_name"]
                )
                logger.info("Deleted subnet group")

            # Delete parameter group
            if "parameter_group_name" in self.created_resources:
                self.redshift_client.delete_cluster_parameter_group(
                    ParameterGroupName=self.created_resources["parameter_group_name"]
                )
                logger.info("Deleted parameter group")

            # Delete security group
            if "security_group_id" in self.created_resources:
                self.ec2_client.delete_security_group(
                    GroupId=self.created_resources["security_group_id"]
                )
                logger.info("Deleted security group")

            # Delete VPC infrastructure
            if "subnet_ids" in self.created_resources:
                for subnet_id in self.created_resources["subnet_ids"]:
                    self.ec2_client.delete_subnet(SubnetId=subnet_id)
                logger.info("Deleted subnets")

            if "route_table_id" in self.created_resources:
                self.ec2_client.delete_route_table(RouteTableId=self.created_resources["route_table_id"])
                logger.info("Deleted route table")

            if ( "internet_gateway_id" in self.created_resources and "vpc_id" in self.created_resources):
                self.ec2_client.detach_internet_gateway(
                    InternetGatewayId=self.created_resources["internet_gateway_id"],
                    VpcId=self.created_resources["vpc_id"],
                )
                self.ec2_client.delete_internet_gateway(
                    InternetGatewayId=self.created_resources["internet_gateway_id"]
                )
                logger.info("Deleted internet gateway")

            if "vpc_id" in self.created_resources:
                self.ec2_client.delete_vpc(VpcId=self.created_resources["vpc_id"])
                logger.info("Deleted VPC")

            # Delete IAM role
            if "iam_role_arn" in self.created_resources:
                role_name = self.created_resources["iam_role_arn"].split("/")[-1]

                # Detach policies
                try:
                    attached_policies = self.iam_client.list_attached_role_policies(
                        RoleName=role_name
                    )
                    for policy in attached_policies["AttachedPolicies"]:
                        self.iam_client.detach_role_policy(
                            RoleName=role_name, PolicyArn=policy["PolicyArn"]
                        )
                except ClientError:
                    pass

                self.iam_client.delete_role(RoleName=role_name)
                logger.info("Deleted IAM role")

            # Delete the VPC Endpoint
            if "vpc_endpoint_id" in self.created_resources:
                self.ec2_client.delete_vpc_endpoints(
                    VpcEndpointIds=[self.creaded_resources["vpc_endpoint_id"]]
                )

            logger.info("Resource cleanup completed")

        except ClientError as e:
            logger.error(f"Error during cleanup: {e}")
            raise

    def serialize_resources(self, file_path=""):

        """
        Saves 'self.created_resources' to a YAML file.

        Args:
            file_path (str): The path of the YAML file to write.
        """
        if not file_path:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            file_path = f"rs_cluster_resources_{timestamp}.yaml"
            file_path = os.path.join(os.getcwd(), file_path)

        try:
            with open(file_path, "w") as yaml_file:
                yaml.dump(self.created_resources, yaml_file, default_flow_style=False)
            logger.info(f"Dictionary saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving to YAML: {e}")


def main():
    """Example usage of the RedshiftClusterManager"""

    # Example configuration
    cluster_config = RedshiftClusterConfig(
        cluster_identifier="my-redshift-cluster",
        master_username="admin",
        master_password="MySecurePassword123!",
        node_type="dc2.large",
        cluster_type="multi-node",
        number_of_nodes=2,
        database_name="analytics",
        publicly_accessible=False,
        encrypted=True,
        automated_snapshot_retention_period=7,
        tags={
            "Environment": "development",
            "Project": "analytics",
            "Owner": "data-team",
        },
    )

    network_config = NetworkConfig(
        vpc_cidr="10.0.0.0/16", subnet_cidrs=["10.0.1.0/24", "10.0.2.0/24"]
    )

    security_config = SecurityConfig(
        allowed_cidr_blocks=["10.0.0.0/16"],  # Only allow access from VPC
        port=5439,
    )

    # Create Redshift environment
    manager = RedshiftClusterManager(region_name="us-east-1")

    try:
        result = manager.create_complete_redshift_environment(
            cluster_config=cluster_config,
            network_config=network_config,
            security_config=security_config,
            resource_prefix="analytics",
            create_iam_role=True,
            create_parameter_group=True,
            parameter_group_parameters={
                "enable_user_activity_logging": "true",
                "max_concurrency_scaling_clusters": "5",
            },
            wait_for_available=True,
        )

        print("Redshift cluster created successfully!")
        print(f"Cluster endpoint: {result['cluster_info']['Endpoint']['Address']}")
        print(f"Cluster port: {result['cluster_info']['Endpoint']['Port']}")

        # Optionally cleanup (uncomment with caution!)
        # manager.cleanup_resources()

    except Exception as e:
        print(f"Error creating Redshift cluster: {e}")
        # Cleanup on error
        # manager.cleanup_resources()


if __name__ == "__main__":
    pass
    # main()

