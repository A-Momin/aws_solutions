import boto3
from botocore.exceptions import ClientError
import os, json, yaml
from datetime import datetime

DB_PASSWORD = os.getenv('DB_PASSWORD')
rds_client = boto3.client('rds')

def create_rds_instance():

    response = rds_client.create_db_instance(
        DBName='tickitdb',                  # Optional, name of the database to create
        DBInstanceIdentifier='mysqlrds2',   # Unique identifier for the DB instance
        Engine='mysql',                     # Example engine, can be 'postgres', 'oracle-se2', etc.
        EngineVersion='8.0.32',             # Example engine version for MySQL
        AllocatedStorage=20,                # Default value is 20 (in GB)
        DBInstanceClass='db.t3.micro',      # Example instance class
        MasterUsername='admin',             # The master username for the DB instance
        MasterUserPassword=DB_PASSWORD,     # The master password for the DB instance
        BackupRetentionPeriod=7,            # Default backup retention period in days
        Port=3306,                          # Default port for MySQL
        MultiAZ=False,                      # Default is single AZ deployment
        AutoMinorVersionUpgrade=True,       # Default value
        PubliclyAccessible=True,            # Whether the DB instance is publicly accessible
        StorageType='gp2',                  # General Purpose SSD (gp2)
        StorageEncrypted=False,             # Default value
        CopyTagsToSnapshot=True,            # Copy tags to snapshots
        EnableIAMDatabaseAuthentication=False,  # Default value
        EnablePerformanceInsights=False,    # Default value
        MonitoringInterval=0,               # Default monitoring interval in seconds
        DeletionProtection=False,           # Default value
        MaxAllocatedStorage=1000,           # Example max allocated storage in GB
        Tags=[
            {
                'Key': 'Name',
                'Value': 'TICKITDB'
            },
        ],
        VpcSecurityGroupIds=[
            'sg-07f4ccd7a5be677ea',  # Example security group ID
        ],
        DBSubnetGroupName='default-vpc-03617a8a518caa526',  # Example subnet group name
        PreferredMaintenanceWindow='Mon:00:00-Mon:03:00',  # Example maintenance window
        PreferredBackupWindow='04:00-05:00',  # Example backup window
    )
    return response


def delete_rds_instance(instance_identifier, region='us-east-1', skip_final_snapshot=True, delete_related_resources=False):
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


# # Usage example
# delete_rds_instance('mysqlrds2')


# # Call the function and print the response
# response = create_rds_instance()
# print(response)
