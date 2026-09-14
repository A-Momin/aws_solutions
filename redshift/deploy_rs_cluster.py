import pickle
import boto3
import os

from misc import load_from_yaml
import s3, iam, lftn, glue, lambdafn as lfn, sns, eventbridge as event, rds, networking

from redshift_manager import (
    RedshiftClusterConfig,
    NetworkConfig,
    SecurityConfig,
    RedshiftClusterManager,
)

from mylogger import CustomLogger
logger = CustomLogger()

#=============================================================================
ACCOUNT_ID = os.environ["AWS_ACCOUNT_ID_ROOT"]
REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

rds_client = boto3.client("rds", region_name=REGION)
iam_client = boto3.client("iam", region_name=REGION)
s3_client = boto3.client("s3", region_name=REGION)
glue_client = boto3.client("glue", region_name=REGION)
lakeformation_client = boto3.client("lakeformation", region_name=REGION)
ec2_client = boto3.client("ec2", region_name=REGION)
ec2_resource = boto3.resource("ec2", region_name=REGION)
events_client = boto3.client("events", region_name=REGION)
lambda_client = boto3.client("lambda", region_name=REGION)

# Create a CloudWatch client for Logs
logs_client = boto3.client("logs", region_name=REGION)

redshift_client = boto3.client("redshift", region_name=REGION)
#=============================================================================
S3_BUCKET_DATALAKE = "htech-datalake-bkt"
S3_BUCKET_GLUE_ASSETS = "htech-glue-assets-bkt"
TEM_DIR = f"s3://{S3_BUCKET_GLUE_ASSETS}/temporary/"
SPARK_EVENT_LOG_PATH = f"s3://{S3_BUCKET_GLUE_ASSETS}/sparkHistoryLogs/"

GLUE_CATALOG_DB = "htech-glue-catalog-db"
DATALAKE_LOCATION_URI = f"s3://{S3_BUCKET_DATALAKE}"

GLUE_ROLE_NAME = "glue-pipeline-role"
LFN_ROLE_NAME = "lfn-pipeline-role"
RS_ROLE_NAME = "dev-rs-role"
GLUE_ROLE_ARN = "arn:aws:iam::530976901147:role/glue-pipeline-role"
LFN_ROLE_ARN = "arn:aws:iam::530976901147:role/lfn-pipeline-role"
RS_ROLE_ARN = "arn:aws:iam::530976901147:role/dev-rs-role"
#=============================================================================
RS_CLUSTER_IDENTIFIER = "dev-rs-cluster"
RS_MASTER_USERNAME = os.environ["USERNAME"]
RS_MASTER_PASSWORD = os.environ["PASSWORD"]
RS_DATABASE_NAME = "dev-rs-db"
GLUE_RS_CONNECTION_NAME = "dev-glue-rs-connection"
RS_CRAWLER_NAME = "dev-rs-sales-tiny-crawler"
#=============================================================================
#=============================================================================

# redshift_client.delete_cluster_subnet_group(
#     ClusterSubnetGroupName="dev-rs-subnet-group"
# )


# =============================================================================
#                     PROVISION REDSHIFT INFRASTRUCTURES
# =============================================================================

cluster_config = RedshiftClusterConfig(
    cluster_identifier=RS_CLUSTER_IDENTIFIER,
    database_name=RS_DATABASE_NAME,
    master_username=RS_MASTER_USERNAME,
    master_password=RS_MASTER_PASSWORD,
    node_type="ra3.xlplus",
    cluster_type="single-node",  # Single node for dev
    publicly_accessible=False,
    encrypted=True,
    automated_snapshot_retention_period=1,  # Shorter retention for dev
    tags={
        "Environment": "development",
        "Team": "HTech",
        "CostCenter": "DE",
    },
)

# More restrictive network for dev
network_config = NetworkConfig(
    vpc_cidr="10.1.0.0/16", subnet_cidrs=["10.1.1.0/24", "10.1.2.0/24"]
)

# Restrictive security - only VPC access
security_config = SecurityConfig(
    allowed_cidr_blocks=["10.1.0.0/16"],
    port=5439,
)

manager = RedshiftClusterManager()

result = manager.create_complete_redshift_environment(
    cluster_config=cluster_config,
    network_config=network_config,
    security_config=security_config,
    resource_prefix="dev-rs",
    create_iam_role=True,
    wait_for_available=True,
)

logger.info(manager.created_resources)

# logger.info(result)
RS_CREATED_RESOURCES_PATH="/Users/am/mydocs/Software_Development/Web_Development/aws/aws_redshift/rs_cluster_resources.yaml"
manager.serialize_resources(RS_CREATED_RESOURCES_PATH)
RS_CREATED_RESOURCES=load_from_yaml(RS_CREATED_RESOURCES_PATH)
logger.info(RS_CREATED_RESOURCES)


# rsql_cmd = """
# COPY SALES
# FROM 's3://htech-datalake-bkt/raw/sales_tiny/'
# IAM_ROLE 'arn:aws:iam::530976901147:role/dev-rs-role'
# IGNOREHEADER 1
# DATEFORMAT 'auto'
# IGNOREBLANKLINES
# DELIMITER ','
# REGION 'us-east-1'
# JOB CREATE JOB_SALES AUTO ON
# """
# errs = "ERROR: Cannot find integration for bucket htech-datalake-bkt [ErrorId: 1-68904001-61b4d48036f96e721728f62b]"
# error = "InvalidInputException: At least one security group must open all ingress ports.To limit traffic, the source security group in your inbound rule can be restricted to the same security group"

# =============================================================================
#                      CREATE AWS GLUE RESOURCES
# =============================================================================

# Construct the connection properties
connection_properties = {
    "USERNAME": RS_MASTER_USERNAME,
    "PASSWORD": RS_MASTER_PASSWORD,
    "JDBC_CONNECTION_URL": manager.created_resources['jdbc_url'],
    "JDBC_ENFORCE_SSL": "false",
}

# Construct the physical connection requirements
physical_connection_requirements = {
    "SecurityGroupIdList": [manager.created_resources["security_group_id"]],
    "SubnetId": manager.created_resources["subnet_ids"][0],
}

response = glue_client.create_connection(
    ConnectionInput={
        "Name": GLUE_RS_CONNECTION_NAME,
        "ConnectionType": "JDBC",  # Use JDBC for Redshift
        "ConnectionProperties": connection_properties,
        "PhysicalConnectionRequirements": physical_connection_requirements,
    },
    Tags={"Name": f"{GLUE_RS_CONNECTION_NAME}"},
)

#==============================================================================
manager.cleanup_resources(
    cluster_identifier=manager.created_resources["cluster_identifier"],
    skip_final_snapshot=True
)

# response = redshift_client.delete_cluster_snapshot(
#     SnapshotIdentifier="rs:dev-rs-cluster-2025-08-04-04-32-48-124"
# )
