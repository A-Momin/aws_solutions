import boto3
from botocore.exceptions import ClientError
import os, json, yaml, subprocess
from datetime import datetime, date
import ec2
from dotenv import load_dotenv

#==============================================================================
ACCOUNT_ID        = os.environ['AWS_ACCOUNT_ID_ROOT']
REGION            = os.environ['AWS_DEFAULT_REGION']
rds_client = boto3.client('rds')
ec2_client           = boto3.client('ec2', region_name=REGION)
ec2_resource         = boto3.resource('ec2', region_name=REGION)
#==============================================================================
VPC_ID            = os.environ['AWS_DEFAULT_VPC']
SECURITY_GROUP_ID = os.environ['AWS_DEFAULT_SG_ID']
SUBNET_IDS        = SUBNET_IDS = os.environ["AWS_DEFAULT_SUBNET_IDS"].split(":")
SUBNET_ID         = SUBNET_IDS[0]
#==============================================================================

DB_NAME = 'EmployeeDB'
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_USERNAME = os.environ['USERNAME']
DB_PASSWORD = os.environ['PASSWORD']
SUBNET_GROUP_NAME = 'httx-rds-subnet-group'
RDS_INSTANCES = [
    {
        'db_instance_identifier': 'httx-rds-mysql',
        'db_name': DB_NAME,
        'db_username': DB_USERNAME,
        'db_password': DB_PASSWORD,
        'engine': 'mysql',
        'port': 3306,
        'engine_version': '8.0.32',
        'db_instance_class': 'db.t3.micro',
        'allocated_storage': 20,
        'availability_zone': 'us-east-1a',
        'tags': [{'Key': 'Project', 'Value': 'glue-rds-Crawler'}],
        'security_group_ids': [SECURITY_GROUP_ID],
        'db_subnet_group_name': SUBNET_GROUP_NAME,
    },
    {
        'db_instance_identifier': 'httx-rds-postgresql',
        'db_name': DB_NAME,
        'db_username': DB_USERNAME,
        'db_password': DB_PASSWORD,
        'port': 5432,
        'engine': 'postgres',
        'engine_version': '14.13',
        'db_instance_class': 'db.t3.micro',
        'allocated_storage': 20,
        'availability_zone': 'us-east-1a',
        'tags': [{'Key': 'Project', 'Value': 'glue-rds-Crawler'}],
        'security_group_ids': [SECURITY_GROUP_ID],
        'db_subnet_group_name': SUBNET_GROUP_NAME,
    },
    {
        'db_instance_identifier': 'httx-rds-mssql',
        'db_name': '',
        'db_username': DB_USERNAME,
        'db_password': DB_PASSWORD,
        'port': 1433,
        'engine': 'sqlserver-ex',
        'engine_version': '15.00.4153.1.v1',
        'db_instance_class': 'db.t3.micro',
        'allocated_storage': 20,
        'availability_zone': 'us-east-1a',
        'tags': [{'Key': 'Project', 'Value': 'glue-rds-Crawler'}],
        'security_group_ids': [SECURITY_GROUP_ID],
        'db_subnet_group_name': SUBNET_GROUP_NAME,
    },
]
# VPC Endpoint parameters
VPC_ENDPOINT_TAG = 'rds-vpc-endpoint' + date.today().strftime('%Y%m%d')
VPC_ENDPOINT_SERVICE_NAME = f"com.amazonaws.{REGION}.s3"
SECURITY_GROUP_IDS = [SECURITY_GROUP_ID]  # Security group(s) associated with the endpoint
ROUTE_TABLE_IDS = ['rtb-0ec4311296ec952f8']
LOAD_DATA_PARAMS={
    "rds_db_endpoint": "",
    "port": "",
    "db_username": "",
    "db_password": "",
    "db_name": "",
    "sql_script_path": ""
}

def create_rds_instance(
    db_instance_identifier, 
    db_name='',
    db_username=os.getenv('USERNAME'), 
    db_password=os.getenv('PASSWORD'), 
    port=3306, 
    engine='mysql', 
    engine_version='8.0.32',
    db_instance_class='db.t3.micro',
    allocated_storage=20,
    availability_zone=f"{REGION}a",
    security_group_ids='sg-0ef97c08a37a1d624',
    db_subnet_group_name='subnet-0980ad10eb313405b'):
    tags=[{'Key': 'rds-cluster','Value': f"{db_instance_identifier}"}],

    response = rds_client.create_db_instance(
        DBName=db_name,                     # Optional, name of the database to create
        DBInstanceIdentifier=db_instance_identifier,   # Unique identifier for the DB instance
        Engine=engine,                      # Example engine, can be 'postgres', 'oracle-se2', etc.
        EngineVersion=engine_version,       # Example engine version for MySQL
        DBInstanceClass=db_instance_class,  # Example instance class
        MasterUsername=db_username,         # The master username for the DB instance
        MasterUserPassword=db_password,     # The master password for the DB instance
        Port=port,                          # Default port for MySQL
        VpcSecurityGroupIds=security_group_ids,
        DBSubnetGroupName=db_subnet_group_name,
        AllocatedStorage=allocated_storage, # Default value is 20 (in GB)
        MultiAZ=False,                      # Default is single AZ deployment
        BackupRetentionPeriod=7,            # Default backup retention period in days
        AutoMinorVersionUpgrade=True,       # Default value
        PubliclyAccessible=True,            # Whether the DB instance is publicly accessible
        StorageType='gp2',                  # General Purpose SSD (gp2)
        StorageEncrypted=False,             # Default value
        CopyTagsToSnapshot=True,            # Copy tags to snapshots
        EnableIAMDatabaseAuthentication=False,  # Default value
        EnablePerformanceInsights=False,    # Default value
        MonitoringInterval=0,               # Default monitoring interval in seconds
        DeletionProtection=False,           # Default value
        MaxAllocatedStorage=100,            # Example max allocated storage in GB
        AvailabilityZone=availability_zone,
        Tags=tags,
        PreferredMaintenanceWindow='Mon:00:00-Mon:03:00',   # Example maintenance window
        PreferredBackupWindow='04:00-05:00',                # Example backup window
    )
    return response

def create_aurora_rds_instance(
    db_instance_identifier,
    db_name,
    master_username,
    master_user_password,
    vpc_security_group_ids,
    db_subnet_group_name,
    db_cluster_identifier,
    engine='aurora-postgresql',
    engine_version='13.7',
    instance_class='db.r5.large',
    storage_encrypted=False,
    allocated_storage=20,
    max_allocated_storage=1000,
    port=5432,
    backup_retention_period=7,
    preferred_backup_window='04:00-05:00',
    preferred_maintenance_window='Mon:00:00-Mon:03:00',
    multi_az=False,
    auto_minor_version_upgrade=True,
    publicly_accessible=True,
    enable_iam_database_authentication=False,
    enable_performance_insights=False,
    monitoring_interval=60,
    monitoring_role_arn=None,
    deletion_protection=False,
    copy_tags_to_snapshot=False,
    tags=None,
    kms_key_id=None,
    region='us-east-1'
    ):
    rds_client = boto3.client('rds', region_name=region)

    # Create the Aurora DB cluster
    response_cluster = rds_client.create_db_cluster(
        DBClusterIdentifier=db_cluster_identifier,
        Engine=engine,
        EngineVersion=engine_version,
        DatabaseName=db_name,
        MasterUsername=master_username,
        MasterUserPassword=master_user_password,
        VpcSecurityGroupIds=vpc_security_group_ids,
        DBSubnetGroupName=db_subnet_group_name,
        BackupRetentionPeriod=backup_retention_period,
        PreferredBackupWindow=preferred_backup_window,
        PreferredMaintenanceWindow=preferred_maintenance_window,
        StorageEncrypted=storage_encrypted,
        KmsKeyId=kms_key_id,
        DeletionProtection=deletion_protection,
        EnableIAMDatabaseAuthentication=enable_iam_database_authentication,
        Tags=tags if tags else []
    )

    # Create the Aurora DB instance
    response_instance = rds_client.create_db_instance(
        DBInstanceIdentifier=db_instance_identifier,
        DBInstanceClass=instance_class,
        Engine=engine,
        DBClusterIdentifier=db_cluster_identifier,
        AllocatedStorage=allocated_storage,
        MaxAllocatedStorage=max_allocated_storage,
        Port=port,
        PubliclyAccessible=publicly_accessible,
        AutoMinorVersionUpgrade=auto_minor_version_upgrade,
        EnablePerformanceInsights=enable_performance_insights,
        MonitoringInterval=monitoring_interval,
        MonitoringRoleArn=monitoring_role_arn,
        CopyTagsToSnapshot=copy_tags_to_snapshot,
        DeletionProtection=deletion_protection,
        MultiAZ=multi_az,
        Tags=tags if tags else []
    )

    return response_cluster, response_instance

def red(s):
    # return '\033[01;31m%s\033[m' % s
    return "\033[01;5m  \033[01;31m %s \033[m  \033[m" % s

def get_rds_endpoint(db_instance_identifier):

    # Describe the RDS instance
    response = rds_client.describe_db_instances(
        DBInstanceIdentifier=db_instance_identifier
    )

    # Extract the instance details
    db_instances = response['DBInstances']
    if db_instances:
        instance = db_instances[0]
        status = instance['DBInstanceStatus']
        
        if status == 'available':
            rds_db_endpoint = instance['Endpoint']['Address']
            print(f"RDS Endpoint: {rds_db_endpoint}")
            return rds_db_endpoint
        else: print(red(f"RDS instance is in {status} state, NO ENDPOINT AVAILABLE YET!!"))
    else:print(red("No RDS instance found."))
    return ''

def delete_rds_instance(instance_identifier, region=REGION, skip_final_snapshot=True, delete_related_resources=False):
    rds_client = boto3.client('rds', region_name=region)
    ec2_client = boto3.client('ec2', region_name=region)
    
    # Get RDS instance details
    try:
        response = rds_client.describe_db_instances(DBInstanceIdentifier=instance_identifier)
        db_instance = response['DBInstances'][0]
    except ClientError as e:
        print(f"Error describing RDS instance: {e}")
        return
    
    # Delete any associated snapshots
    try:
        snapshots = rds_client.describe_db_snapshots(DBInstanceIdentifier=instance_identifier)['DBSnapshots']
        for snapshot in snapshots:
            snapshot_id = snapshot['DBSnapshotIdentifier']
            rds_client.delete_db_snapshot(DBSnapshotIdentifier=snapshot_id)
            print(f"Deleted snapshot: {snapshot_id}")
    except ClientError as e:
        print(f"Error deleting snapshots: {e}")
    
    # Delete the RDS instance
    try:
        rds_client.delete_db_instance(
            DBInstanceIdentifier=instance_identifier,
            SkipFinalSnapshot=skip_final_snapshot
        )
        print(f"Deleted RDS instance: {instance_identifier}")
    except ClientError as e:
        print(f"Error deleting RDS instance: {e}")
    
    if delete_related_resources:
        # Delete security groups
        vpc_security_groups = db_instance['VpcSecurityGroups']
        for sg in vpc_security_groups:
            sg_id = sg['VpcSecurityGroupId']
            try:
                ec2_client.delete_security_group(GroupId=sg_id)
                print(f"Deleted security group: {sg_id}")
            except ClientError as e:
                print(f"Error deleting security group {sg_id}: {e}")
        
        # Delete DB subnet group
        db_subnet_group_name = db_instance['DBSubnetGroup']['DBSubnetGroupName']
        try:
            rds_client.delete_db_subnet_group(DBSubnetGroupName=db_subnet_group_name)
            print(f"Deleted DB subnet group: {db_subnet_group_name}")
        except ClientError as e:
            print(f"Error deleting DB subnet group {db_subnet_group_name}: {e}")

def get_rds_instance_parameters(instance_identifier):
    rds = boto3.client('rds')
    
    # Describe the RDS instance
    response = rds.describe_db_instances(
        DBInstanceIdentifier=instance_identifier
    )
    
    if response['DBInstances']:
        return response['DBInstances'][0]
    else:
        raise Exception(f'No RDS instance found with identifier {instance_identifier}')

def datetime_serializer(o):
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError(f"Type {type(o)} not serializable")

def load_data_into_rds(**kwargs):
    """
    Loads data into an RDS instance by executing a SQL script.

    Args:
        **kwargs: Arbitrary keyword arguments, expected to include:
            rds_db_endpoint (str): The endpoint of the RDS SQL instance.
            port (str): The port number for the SQL connection.
            db_username (str): The username for the SQL database.
            db_password (str): The password for the SQL database.
            db_name (str): The name of the database to connect to.
            sql_script_path (str): The path to the SQL script to be executed.

    Raises:
        subprocess.CalledProcessError: If the SQL command fails.
    
    Returns:
        None
    
    Equivalent SQL Command:
        mysql -h {mysql_endpoint} -P {instances[0]['port']} -u {DB_USERNAME} -p'{DB_PASSWORD}' {DB_NAME} < ./mysql_employees.sql
    """
    # Construct the MySQL command
    command = [
        "mysql",
        "-h", kwargs['rds_db_endpoint'],
        "-P", kwargs['port'],
        "-u", kwargs['db_username'],
        f"-p{kwargs['db_password']}",
        kwargs['db_name'],
        "-e", f"source {kwargs['sql_script_path']}"
    ]

    # Execute the command
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print("SQL script executed successfully.")
        print("Output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error while executing the SQL script.")
        print("Error:", e.stderr)

def create_subnet_group(subnet_group_name="rds_subnet_group", subnet_ids=SUBNET_IDS):
    ## Create the RDS subnet group
    response = rds_client.create_db_subnet_group(
        DBSubnetGroupName=subnet_group_name,
        DBSubnetGroupDescription='Subnet group for RDS instance',
        SubnetIds=subnet_ids
    )
    return response
    print(response)

def create_rds_with_dependencies():


    [create_rds_instance(**instance_param) for instance_param in RDS_INSTANCES]

    load_data_into_rds(**LOAD_DATA_PARAMS)

    # Create an Interface Endpoint
    VPC_ENDPOINT_ID = ec2_client.create_vpc_endpoint(
        VpcEndpointType='Gateway',
        VpcId=VPC_ID,
        ServiceName=VPC_ENDPOINT_SERVICE_NAME,
        RouteTableIds=ROUTE_TABLE_IDS,
        # SubnetIds=sg_id,
        # SecurityGroupIds=security_group_ids,
        PrivateDnsEnabled=False  # Enable private DNS to resolve service names within the VPC
    )['VpcEndpoint']['VpcEndpointId']

    vpc_endpoints = ec2_client.describe_vpc_endpoints(
        Filters=[
            {'Name': 'vpc-id', 'Values': [VPC_ID]},
            {'Name': 'service-name', 'Values': [VPC_ENDPOINT_SERVICE_NAME]}
        ]
    )
    print(vpc_endpoints['VpcEndpoints'][0]['VpcEndpointId'])

    ec2_client.create_tags(Resources=[VPC_ENDPOINT_ID],Tags=[{'Key': 'Name', 'Value': VPC_ENDPOINT_TAG}])


    


# if __name__ == '__main__':

#     # # Usage example
#     # delete_rds_instance('mysqlrds2')

#     # # Call the function and print the response
#     # response = create_rds_instance()
#     # print(response)

    # Example usage
    response_cluster, response_instance = create_aurora_rds_instance(
        db_cluster_identifier='my-aurora-cluster',
        db_instance_identifier='my-aurora-instance',
        db_name='mydatabase',
        master_username='myusername',
        master_user_password='mypassword',
        vpc_security_group_ids=['sg-0123456789abcdef0'],
        db_subnet_group_name='my-db-subnet-group',
        region='us-east-1',
        tags=[
            {'Key': 'Name', 'Value': 'MyAuroraDB'},
            {'Key': 'Environment', 'Value': 'Production'}
        ]
    )

    print('Cluster Response:', response_cluster)
    print('Instance Response:', response_instance)
