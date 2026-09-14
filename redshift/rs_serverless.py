import boto3
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ResourceStatus(Enum):
    """Status of AWS resources"""

    CREATING = "CREATING"
    AVAILABLE = "AVAILABLE"
    DELETING = "DELETING"
    DELETED = "DELETED"
    FAILED = "FAILED"


@dataclass
class RedshiftServerlessConfig:
    """Configuration for Redshift Serverless"""

    namespace_name: str
    workgroup_name: str
    database_name: str
    admin_username: str
    admin_password: str
    base_capacity: int = 32
    region: str = "us-east-1"

    # VPC Configuration
    vpc_cidr: str = "10.0.0.0/16"
    subnet_cidrs: List[str] = None
    availability_zones: List[str] = None

    # Security
    publicly_accessible: bool = False

    def __post_init__(self):
        if self.subnet_cidrs is None:
            self.subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24"]
        if self.availability_zones is None:
            self.availability_zones = [f"{self.region}a", f"{self.region}b"]


class RedshiftServerlessManager:
    """Manager class for Amazon Redshift Serverless resources"""

    def __init__(
        self, config: RedshiftServerlessConfig, profile_name: Optional[str] = None
    ):
        self.config = config
        self.profile_name = profile_name
        self.session = self._create_session()

        # Initialize AWS clients
        self.redshift_serverless = self.session.client(
            "redshift-serverless", region_name=config.region
        )
        self.ec2 = self.session.client("ec2", region_name=config.region)
        self.iam = self.session.client("iam")

        # Resource tracking
        self.created_resources = {
            "vpc_id": None,
            "subnet_ids": [],
            "security_group_id": None,
            "internet_gateway_id": None,
            "route_table_id": None,
            "iam_role_arn": None,
            "namespace_name": None,
            "workgroup_name": None,
        }

    def _create_session(self) -> boto3.Session:
        """Create boto3 session"""
        if self.profile_name:
            return boto3.Session(profile_name=self.profile_name)
        return boto3.Session()

    def _wait_for_resource(
        self, check_function, resource_name: str, timeout: int = 600, interval: int = 30
    ):
        """Wait for a resource to be ready"""
        logger.info(f"Waiting for {resource_name} to be ready...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                if check_function():
                    logger.info(f"{resource_name} is ready")
                    return True
            except Exception as e:
                logger.warning(f"Error checking {resource_name} status: {e}")

            time.sleep(interval)

        raise TimeoutError(
            f"{resource_name} did not become ready within {timeout} seconds"
        )

    def create_vpc_resources(self) -> Dict[str, Any]:
        """Create VPC and related networking resources"""
        logger.info("Creating VPC resources...")

        try:
            # Create VPC
            vpc_response = self.ec2.create_vpc(
                CidrBlock=self.config.vpc_cidr,
                EnableDnsHostnames=True,
                EnableDnsSupport=True,
            )
            vpc_id = vpc_response["Vpc"]["VpcId"]
            self.created_resources["vpc_id"] = vpc_id

            # Tag VPC
            self.ec2.create_tags(
                Resources=[vpc_id],
                Tags=[
                    {"Key": "Name", "Value": f"{self.config.namespace_name}-vpc"},
                    {"Key": "Purpose", "Value": "RedshiftServerless"},
                ],
            )

            # Create Internet Gateway
            igw_response = self.ec2.create_internet_gateway()
            igw_id = igw_response["InternetGateway"]["InternetGatewayId"]
            self.created_resources["internet_gateway_id"] = igw_id

            # Attach Internet Gateway to VPC
            self.ec2.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)

            # Create subnets
            subnet_ids = []
            for i, (cidr, az) in enumerate(
                zip(self.config.subnet_cidrs, self.config.availability_zones)
            ):
                subnet_response = self.ec2.create_subnet(
                    VpcId=vpc_id, CidrBlock=cidr, AvailabilityZone=az
                )
                subnet_id = subnet_response["Subnet"]["SubnetId"]
                subnet_ids.append(subnet_id)

                # Tag subnet
                self.ec2.create_tags(
                    Resources=[subnet_id],
                    Tags=[
                        {
                            "Key": "Name",
                            "Value": f"{self.config.namespace_name}-subnet-{i + 1}",
                        },
                        {"Key": "Purpose", "Value": "RedshiftServerless"},
                    ],
                )

            self.created_resources["subnet_ids"] = subnet_ids

            # Create route table
            route_table_response = self.ec2.create_route_table(VpcId=vpc_id)
            route_table_id = route_table_response["RouteTable"]["RouteTableId"]
            self.created_resources["route_table_id"] = route_table_id

            # Create route to Internet Gateway
            self.ec2.create_route(
                RouteTableId=route_table_id,
                DestinationCidrBlock="0.0.0.0/0",
                GatewayId=igw_id,
            )

            # Associate subnets with route table
            for subnet_id in subnet_ids:
                self.ec2.associate_route_table(
                    RouteTableId=route_table_id, SubnetId=subnet_id
                )

            # Create security group
            sg_response = self.ec2.create_security_group(
                GroupName=f"{self.config.namespace_name}-sg",
                Description="Security group for Redshift Serverless",
                VpcId=vpc_id,
            )
            sg_id = sg_response["GroupId"]
            self.created_resources["security_group_id"] = sg_id

            # Add inbound rule for Redshift (port 5439)
            self.ec2.authorize_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=[
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 5439,
                        "ToPort": 5439,
                        "IpRanges": [
                            {"CidrIp": "0.0.0.0/0", "Description": "Redshift access"}
                        ],
                    }
                ],
            )

            logger.info("VPC resources created successfully")
            return {
                "vpc_id": vpc_id,
                "subnet_ids": subnet_ids,
                "security_group_id": sg_id,
                "internet_gateway_id": igw_id,
                "route_table_id": route_table_id,
            }

        except Exception as e:
            logger.error(f"Failed to create VPC resources: {e}")
            raise

    def create_iam_role(self) -> str:
        """Create IAM role for Redshift Serverless"""
        logger.info("Creating IAM role...")

        role_name = f"{self.config.namespace_name}-redshift-role"

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

        try:
            # Create IAM role
            role_response = self.iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description="IAM role for Redshift Serverless",
                Tags=[
                    {"Key": "Purpose", "Value": "RedshiftServerless"},
                    {"Key": "Namespace", "Value": self.config.namespace_name},
                ],
            )

            role_arn = role_response["Role"]["Arn"]
            self.created_resources["iam_role_arn"] = role_arn

            # Attach managed policies
            managed_policies = [
                "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess",
                "arn:aws:iam::aws:policy/AmazonRedshiftAllCommandsFullAccess",
            ]

            for policy_arn in managed_policies:
                self.iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)

            logger.info(f"IAM role created: {role_arn}")
            return role_arn

        except Exception as e:
            logger.error(f"Failed to create IAM role: {e}")
            raise

    def create_namespace(self) -> Dict[str, Any]:
        """Create Redshift Serverless namespace"""
        logger.info("Creating Redshift Serverless namespace...")

        try:
            response = self.redshift_serverless.create_namespace(
                namespaceName=self.config.namespace_name,
                adminUsername=self.config.admin_username,
                adminUserPassword=self.config.admin_password,
                dbName=self.config.database_name,
                defaultIamRoleArn=self.created_resources["iam_role_arn"],
                tags=[
                    {"key": "Purpose", "value": "RedshiftServerless"},
                    {"key": "Environment", "value": "Development"},
                ],
            )

            self.created_resources["namespace_name"] = self.config.namespace_name

            # Wait for namespace to be available
            def check_namespace():
                try:
                    ns_response = self.redshift_serverless.get_namespace(
                        namespaceName=self.config.namespace_name
                    )
                    return ns_response["namespace"]["status"] == "AVAILABLE"
                except:
                    return False

            self._wait_for_resource(check_namespace, "namespace")

            logger.info("Namespace created successfully")
            return response["namespace"]

        except Exception as e:
            logger.error(f"Failed to create namespace: {e}")
            raise

    def create_workgroup(self) -> Dict[str, Any]:
        """Create Redshift Serverless workgroup"""
        logger.info("Creating Redshift Serverless workgroup...")

        try:
            response = self.redshift_serverless.create_workgroup(
                workgroupName=self.config.workgroup_name,
                namespaceName=self.config.namespace_name,
                baseCapacity=self.config.base_capacity,
                publiclyAccessible=self.config.publicly_accessible,
                subnetIds=self.created_resources["subnet_ids"],
                securityGroupIds=[self.created_resources["security_group_id"]],
                tags=[
                    {"key": "Purpose", "value": "RedshiftServerless"},
                    {"key": "Environment", "value": "Development"},
                ],
            )

            self.created_resources["workgroup_name"] = self.config.workgroup_name

            # Wait for workgroup to be available
            def check_workgroup():
                try:
                    wg_response = self.redshift_serverless.get_workgroup(
                        workgroupName=self.config.workgroup_name
                    )
                    return wg_response["workgroup"]["status"] == "AVAILABLE"
                except:
                    return False

            self._wait_for_resource(check_workgroup, "workgroup")

            logger.info("Workgroup created successfully")
            return response["workgroup"]

        except Exception as e:
            logger.error(f"Failed to create workgroup: {e}")
            raise

    def create_all_resources(self) -> Dict[str, Any]:
        """Create all Redshift Serverless resources"""
        logger.info("Starting Redshift Serverless deployment...")

        try:
            # Step 1: Create VPC resources
            vpc_resources = self.create_vpc_resources()

            # Step 2: Create IAM role
            iam_role_arn = self.create_iam_role()

            # Step 3: Create namespace
            namespace = self.create_namespace()

            # Step 4: Create workgroup
            workgroup = self.create_workgroup()

            # Get connection info
            connection_info = self.get_connection_info()

            logger.info("Redshift Serverless deployment completed successfully!")

            return {
                "vpc_resources": vpc_resources,
                "iam_role_arn": iam_role_arn,
                "namespace": namespace,
                "workgroup": workgroup,
                "connection_info": connection_info,
                "created_resources": self.created_resources,
            }

        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            logger.info("Attempting to clean up resources...")
            self.delete_all_resources()
            raise

    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information for the Redshift Serverless cluster"""
        try:
            workgroup_response = self.redshift_serverless.get_workgroup(
                workgroupName=self.config.workgroup_name
            )

            workgroup = workgroup_response["workgroup"]
            endpoint = workgroup.get("endpoint", {})

            return {
                "endpoint": endpoint.get("address"),
                "port": endpoint.get("port", 5439),
                "database": self.config.database_name,
                "username": self.config.admin_username,
                "workgroup_name": self.config.workgroup_name,
                "namespace_name": self.config.namespace_name,
            }

        except Exception as e:
            logger.error(f"Failed to get connection info: {e}")
            return {}

    def delete_workgroup(self):
        """Delete Redshift Serverless workgroup"""
        if not self.created_resources["workgroup_name"]:
            return

        logger.info("Deleting workgroup...")
        try:
            self.redshift_serverless.delete_workgroup(
                workgroupName=self.created_resources["workgroup_name"]
            )

            # Wait for workgroup to be deleted
            def check_workgroup_deleted():
                try:
                    self.redshift_serverless.get_workgroup(
                        workgroupName=self.created_resources["workgroup_name"]
                    )
                    return False  # Still exists
                except self.redshift_serverless.exceptions.ResourceNotFoundException:
                    return True  # Deleted
                except:
                    return False

            self._wait_for_resource(check_workgroup_deleted, "workgroup deletion")
            logger.info("Workgroup deleted successfully")

        except Exception as e:
            logger.error(f"Failed to delete workgroup: {e}")

    def delete_namespace(self):
        """Delete Redshift Serverless namespace"""
        if not self.created_resources["namespace_name"]:
            return

        logger.info("Deleting namespace...")
        try:
            self.redshift_serverless.delete_namespace(
                namespaceName=self.created_resources["namespace_name"]
            )

            # Wait for namespace to be deleted
            def check_namespace_deleted():
                try:
                    self.redshift_serverless.get_namespace(
                        namespaceName=self.created_resources["namespace_name"]
                    )
                    return False  # Still exists
                except self.redshift_serverless.exceptions.ResourceNotFoundException:
                    return True  # Deleted
                except:
                    return False

            self._wait_for_resource(check_namespace_deleted, "namespace deletion")
            logger.info("Namespace deleted successfully")

        except Exception as e:
            logger.error(f"Failed to delete namespace: {e}")

    def delete_iam_role(self):
        """Delete IAM role"""
        if not self.created_resources["iam_role_arn"]:
            return

        logger.info("Deleting IAM role...")
        role_name = f"{self.config.namespace_name}-redshift-role"

        try:
            # Detach managed policies
            managed_policies = [
                "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess",
                "arn:aws:iam::aws:policy/AmazonRedshiftAllCommandsFullAccess",
            ]

            for policy_arn in managed_policies:
                try:
                    self.iam.detach_role_policy(
                        RoleName=role_name, PolicyArn=policy_arn
                    )
                except:
                    pass

            # Delete role
            self.iam.delete_role(RoleName=role_name)
            logger.info("IAM role deleted successfully")

        except Exception as e:
            logger.error(f"Failed to delete IAM role: {e}")

    def delete_vpc_resources(self):
        """Delete VPC and related resources"""
        logger.info("Deleting VPC resources...")

        try:
            # Delete security group
            if self.created_resources["security_group_id"]:
                try:
                    self.ec2.delete_security_group(
                        GroupId=self.created_resources["security_group_id"]
                    )
                except Exception as e:
                    logger.warning(f"Failed to delete security group: {e}")

            # Delete subnets
            for subnet_id in self.created_resources["subnet_ids"]:
                try:
                    self.ec2.delete_subnet(SubnetId=subnet_id)
                except Exception as e:
                    logger.warning(f"Failed to delete subnet {subnet_id}: {e}")

            # Delete route table
            if self.created_resources["route_table_id"]:
                try:
                    self.ec2.delete_route_table(
                        RouteTableId=self.created_resources["route_table_id"]
                    )
                except Exception as e:
                    logger.warning(f"Failed to delete route table: {e}")

            # Detach and delete internet gateway
            if (
                self.created_resources["internet_gateway_id"]
                and self.created_resources["vpc_id"]
            ):
                try:
                    self.ec2.detach_internet_gateway(
                        InternetGatewayId=self.created_resources["internet_gateway_id"],
                        VpcId=self.created_resources["vpc_id"],
                    )
                    self.ec2.delete_internet_gateway(
                        InternetGatewayId=self.created_resources["internet_gateway_id"]
                    )
                except Exception as e:
                    logger.warning(f"Failed to delete internet gateway: {e}")

            # Delete VPC
            if self.created_resources["vpc_id"]:
                try:
                    self.ec2.delete_vpc(VpcId=self.created_resources["vpc_id"])
                except Exception as e:
                    logger.warning(f"Failed to delete VPC: {e}")

            logger.info("VPC resources deleted successfully")

        except Exception as e:
            logger.error(f"Failed to delete VPC resources: {e}")

    def delete_all_resources(self):
        """Delete all created resources"""
        logger.info("Starting resource cleanup...")

        # Delete in reverse order of creation
        self.delete_workgroup()
        self.delete_namespace()
        self.delete_iam_role()

        # Wait a bit before deleting VPC resources
        time.sleep(30)
        self.delete_vpc_resources()

        logger.info("Resource cleanup completed")

    def get_status(self) -> Dict[str, Any]:
        """Get status of all resources"""
        status = {}

        try:
            # Namespace status
            if self.created_resources["namespace_name"]:
                ns_response = self.redshift_serverless.get_namespace(
                    namespaceName=self.created_resources["namespace_name"]
                )
                status["namespace"] = ns_response["namespace"]["status"]
        except:
            status["namespace"] = "NOT_FOUND"

        try:
            # Workgroup status
            if self.created_resources["workgroup_name"]:
                wg_response = self.redshift_serverless.get_workgroup(
                    workgroupName=self.created_resources["workgroup_name"]
                )
                status["workgroup"] = wg_response["workgroup"]["status"]
        except:
            status["workgroup"] = "NOT_FOUND"

        return status


def main():
    """Main function to demonstrate usage"""

    # Configuration
    config = RedshiftServerlessConfig(
        namespace_name="my-redshift-namespace",
        workgroup_name="my-redshift-workgroup",
        database_name="dev",
        admin_username="admin",
        admin_password="MySecurePassword123!",
        base_capacity=32,
        region="us-east-1",
        publicly_accessible=False,
    )

    # Create manager
    manager = RedshiftServerlessManager(config)

    try:
        # Create all resources
        result = manager.create_all_resources()

        print("\n" + "=" * 50)
        print("REDSHIFT SERVERLESS DEPLOYMENT SUCCESSFUL")
        print("=" * 50)

        connection_info = result["connection_info"]
        print(f"Endpoint: {connection_info.get('endpoint')}")
        print(f"Port: {connection_info.get('port')}")
        print(f"Database: {connection_info.get('database')}")
        print(f"Username: {connection_info.get('username')}")
        print(f"Workgroup: {connection_info.get('workgroup_name')}")
        print(f"Namespace: {connection_info.get('namespace_name')}")

        print("\nConnection string example:")
        print(
            f"postgresql://{connection_info.get('username')}:<password>@{connection_info.get('endpoint')}:{connection_info.get('port')}/{connection_info.get('database')}"
        )

        # Uncomment the following line to delete resources immediately
        # manager.delete_all_resources()

    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())


# # Basic usage
# config = RedshiftServerlessConfig(
#     namespace_name="my-namespace",
#     workgroup_name="my-workgroup",
#     database_name="dev",
#     admin_username="admin",
#     admin_password="SecurePassword123!",
# )

# manager = RedshiftServerlessManager(config)

# # Create all resources
# result = manager.create_all_resources()

# # Get connection info
# connection_info = manager.get_connection_info()

# # Check status
# status = manager.get_status()

# # Clean up all resources
# manager.delete_all_resources()
