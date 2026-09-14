
import boto3
import os

ACCOUNT_ID        = os.environ['AWS_ACCOUNT_ID_ROOT']
REGION            = os.environ['AWS_DEFAULT_REGION']
VPC_ID            = os.environ['AWS_DEFAULT_VPC']
SECURITY_GROUP_ID = os.environ['AWS_DEFAULT_SG_ID']
SUBNET_IDS        = SUBNET_IDS = os.environ["AWS_DEFAULT_SUBNET_IDS"].split(":")
SUBNET_ID         = SUBNET_IDS[0]

#=============================================================================
# Create a Redshift client
redshift_client = boto3.client('redshift', region_name=REGION)  # specify your region
#=============================================================================

REDSHIFT_CLUSTER_PARAMS={
    "DBName": 'db_name',
    "ClusterIdentifier": 'identifier',
    "ClusterType": 'single-node',
    "NodeType": 'dc2.large',
    "MasterUsername": 'db_user_name',
    "MasterUserPassword": 'db_password',
    "ClusterSecurityGroups": ['string',],
    "VpcSecurityGroupIds": ['string',],
    "ClusterSubnetGroupName": 'string',
    "AvailabilityZone": 'string',
    "PreferredMaintenanceWindow": 'Mon:03:00-Mon:04:00',
    "ClusterParameterGroupName": 'string',
    "AutomatedSnapshotRetentionPeriod": 7,
    "ManualSnapshotRetentionPeriod": 7,
    "Port": 5439,
    "ClusterVersion": 'string',
    "AllowVersionUpgrade": True,
    "NumberOfNodes": 1,
    "PubliclyAccessible": True,
    "Encrypted": False,
    "HsmClientCertificateIdentifier": 'string',
    "HsmConfigurationIdentifier": 'string',
    "ElasticIp": 'string',
    "Tags": [
        {'Key': 'Name', 'Value': 'htech-rs-cluster'},
        {'Key': 'Environment', 'Value': 'Dev'}
    ],
    "KmsKeyId": 'string',
    # "EnhancedVpcRouting": True,
    # "AdditionalInfo": 'string',
    # "IamRoles": ['string',],
    # "MaintenanceTrackName": 'string',
    "SnapshotScheduleIdentifier": 'htech-snapshot-schedule',
    # "AvailabilityZoneRelocation": True,
    # "AquaConfigurationStatus": 'enabled',   # |'disabled'|'auto',
    # "DefaultIamRoleArn": 'string',
    # "LoadSampleData": 'string',
    # "ManageMasterPassword": True,
    # "MasterPasswordSecretKmsKeyId": 'string',
    # "IpAddressType": 'string',
    # "MultiAZ": True,
    # "RedshiftIdcApplicationArn": 'string'
}


# NOT TESTED!
def create_redshift_cluster_v2(identifier, db_name, db_user_name, db_password, num_nodes=1):

    response = redshift_client.create_cluster(
        DBName=db_name,  # Name of the primary database to be created in the cluster.
        ClusterIdentifier=identifier,  # Unique identifier for the cluster. Must be unique within the AWS account.
        ClusterType='string',  # Type of the cluster. Options: 'single-node' for a single-node cluster or 'multi-node' for a multi-node cluster.
        NodeType='string',  # Type of node to be provisioned (e.g., 'dc2.large', 'ra3.xlplus'). Determines the performance and cost.
        MasterUsername=db_user_name,  # Username for the master user with superuser permissions in the database.
        MasterUserPassword=db_password,  # Password for the master user. Must meet AWS password requirements.
        ClusterSecurityGroups=['string',],  # A list of cluster security groups to associate with the cluster.
        VpcSecurityGroupIds=['string',],  # A list of VPC security group IDs to associate with the cluster for network access control.
        ClusterSubnetGroupName='string',  # The name of the subnet group to use for the cluster (for placement within a specific VPC).
        AvailabilityZone='string',  # The specific Availability Zone in which to launch the cluster (optional).
        PreferredMaintenanceWindow='string',  # Weekly time range for maintenance (e.g., "Mon:09:00-Mon:10:00").
        ClusterParameterGroupName='string',  # Name of the parameter group to apply to the cluster, defining cluster settings.
        AutomatedSnapshotRetentionPeriod=123,  # Number of days to retain automated snapshots (0 disables snapshots).
        ManualSnapshotRetentionPeriod=123,  # Number of days to retain manual snapshots (useful for long-term backups).
        Port=5439,  # Port number on which the cluster accepts connections (default: 5439 for Redshift).
        ClusterVersion='string',  # Version of the Redshift engine to use (e.g., '1.0' or 'latest').
        AllowVersionUpgrade=True|False,  # Whether the cluster is automatically upgraded to new engine versions (default: True).
        NumberOfNodes=num_nodes,  # Number of compute nodes in the cluster (required for multi-node clusters).
        PubliclyAccessible=True|False,  # Whether the cluster is accessible from a public IP address.
        Encrypted=True|False,  # Whether the data at rest in the cluster is encrypted.
        HsmClientCertificateIdentifier='string',  # Identifier of the HSM client certificate for encryption keys (if using HSM).
        HsmConfigurationIdentifier='string',  # Identifier of the HSM configuration to be used with the cluster.
        ElasticIp='string',  # Elastic IP address to associate with the cluster (for a publicly accessible cluster).
        Tags=[{'Key': 'string', 'Value': 'string'},],  # Key-value pairs for tagging the cluster (for organization and tracking).
        KmsKeyId='string',  # AWS KMS key ID to use for encrypting data at rest in the cluster.
        EnhancedVpcRouting=True|False,  # Whether enhanced VPC routing is enabled (for network traffic management).
        AdditionalInfo='string',  # Reserved for additional information about the cluster (used internally).
        IamRoles=['string',],  # List of IAM role ARNs to associate with the cluster for granting access to AWS services.
        MaintenanceTrackName='string',  # Name of the maintenance track for the cluster (e.g., 'current' or 'trailing').
        SnapshotScheduleIdentifier='string',  # Identifier of the snapshot schedule to associate with the cluster.
        AvailabilityZoneRelocation=True|False,  # Whether to allow relocation to another availability zone during maintenance.
        AquaConfigurationStatus='enabled'|'disabled'|'auto',  # AQUA configuration status for query acceleration ('auto' recommended).
        DefaultIamRoleArn='string',  # ARN of the default IAM role to be associated with the cluster.
        LoadSampleData='string',  # Option to load sample data into the cluster ('tickit' is commonly used).
        ManageMasterPassword=True|False,  # Whether the master password is managed automatically by AWS Secrets Manager.
        MasterPasswordSecretKmsKeyId='string',  # KMS key ID used to encrypt the master password in Secrets Manager.
        IpAddressType='string',  # Type of IP address to assign to the cluster ('ipv4' or other supported values).
        MultiAZ=True|False,  # Whether the cluster is set up for multi-AZ deployment for higher availability.
        RedshiftIdcApplicationArn='string'  # ARN of the Amazon Redshift-integrated IDC application (if applicable).
    )


# NOT WORKING!
def create_redshift_cluster_v3(
    db_name="HTech-REDSHIFT-DB",  # Default database name
    cluster_identifier="HTech-REDSHIFT-CLUSTER",  # Unique cluster identifier
    cluster_type="multi-node",  # Cluster type: 'single-node' or 'multi-node'
    node_type="dc2.large",  # Default node type
    master_username=os.environ['USERNAME'],  # Default master username
    master_user_password=os.environ['PASSWORD'],  # Default master password
    # cluster_security_groups=[],  # List of cluster security group names
    vpc_security_group_ids=[],  # List of VPC security group IDs
    # cluster_subnet_group_name='',  # Subnet group name for cluster
    # availability_zone='',  # AZ in which the cluster is created
    preferred_maintenance_window='',  # Maintenance window (e.g., "Mon:09:00-Mon:10:00")
    cluster_parameter_group_name='',  # Cluster parameter group name
    automated_snapshot_retention_period=1,  # Retain automated snapshots (days)
    manual_snapshot_retention_period=1,  # Retain manual snapshots (days)
    port=5439,  # Port for database connections
    cluster_version='',  # Redshift engine version
    allow_version_upgrade=True,  # Allow automatic version upgrades
    number_of_nodes=2,  # Number of nodes (required for multi-node clusters)
    publicly_accessible=False,  # Whether the cluster is publicly accessible
    encrypted=False,  # Encrypt data at rest
    # hsm_client_certificate_identifier='',  # HSM client certificate
    # hsm_configuration_identifier='',  # HSM configuration
    # elastic_ip='',  # Elastic IP address
    tags=[],  # List of tags (e.g., [{'Key': 'Name', 'Value': 'MyCluster'}])
    # kms_key_id='',  # AWS KMS key for encryption
    enhanced_vpc_routing=False,  # Enable enhanced VPC routing
    # additional_info='',  # Reserved for internal use
    iam_roles=[],  # List of IAM roles for Redshift to assume
    maintenance_track_name='',  # Maintenance track (e.g., 'current' or 'trailing')
    snapshot_schedule_identifier='',  # Snapshot schedule ID
    availability_zone_relocation=False,  # Allow relocation across AZs
    aqua_configuration_status="auto",  # AQUA settings: 'enabled', 'disabled', 'auto'
    default_iam_role_arn='',  # Default IAM role ARN
    load_sample_data='tickit',  # Option to load sample data (e.g., 'tickit')
    manage_master_password=False,  # Whether AWS Secrets Manager manages the master password
    master_password_secret_kms_key_id='',  # KMS key for encrypting Secrets Manager password
    ip_address_type="ipv4",  # IP address type ('ipv4' or others)
    multi_az=False,  # Multi-AZ deployment
    redshift_idc_application_arn='',  # ARN of IDC application (if applicable)
    ):
    try:
        # Initialize Redshift client
        redshift_client = boto3.client('redshift')

        # Create cluster
        response = redshift_client.create_cluster(
            DBName=db_name,
            ClusterIdentifier=cluster_identifier,
            ClusterType=cluster_type,
            NodeType=node_type,
            MasterUsername=master_username,
            MasterUserPassword=master_user_password,
            # ClusterSecurityGroups=cluster_security_groups or [], # Cannot use both cluster security groups and VPC security groups
            VpcSecurityGroupIds=vpc_security_group_ids or [],
            # ClusterSubnetGroupName=cluster_subnet_group_name,
            # AvailabilityZone=availability_zone,
            PreferredMaintenanceWindow=preferred_maintenance_window,
            ClusterParameterGroupName=cluster_parameter_group_name,
            AutomatedSnapshotRetentionPeriod=automated_snapshot_retention_period,
            ManualSnapshotRetentionPeriod=manual_snapshot_retention_period,
            Port=port,
            ClusterVersion=cluster_version,
            AllowVersionUpgrade=allow_version_upgrade,
            NumberOfNodes=number_of_nodes if cluster_type == "multi-node" else 1,
            PubliclyAccessible=publicly_accessible,
            Encrypted=encrypted,
            # HsmClientCertificateIdentifier=hsm_client_certificate_identifier,
            # HsmConfigurationIdentifier=hsm_configuration_identifier,
            # ElasticIp=elastic_ip,
            Tags=tags or [],
            # KmsKeyId=kms_key_id,
            EnhancedVpcRouting=enhanced_vpc_routing,
            # AdditionalInfo=additional_info,
            IamRoles=iam_roles or [],
            MaintenanceTrackName=maintenance_track_name,
            SnapshotScheduleIdentifier=snapshot_schedule_identifier,
            AvailabilityZoneRelocation=availability_zone_relocation,
            AquaConfigurationStatus=aqua_configuration_status,
            DefaultIamRoleArn=default_iam_role_arn,
            LoadSampleData=load_sample_data,
            ManageMasterPassword=manage_master_password,
            MasterPasswordSecretKmsKeyId=master_password_secret_kms_key_id,
            IpAddressType=ip_address_type,
            MultiAZ=multi_az,
            RedshiftIdcApplicationArn=redshift_idc_application_arn,
        )

        # Return response
        return response

    except Exception as e:
        print(f"Error creating Redshift cluster: {e}")
        return None


def create_redshift_subnet_group(subnet_group_name="redshift_subnet_group", subnet_ids=SUBNET_IDS, description="A Redshift subnet group for my clusters"):
    """
    Creates an AWS Redshift Subnet Group.

    Args:
        subnet_group_name (str): The name of the subnet group.
        description (str): A description of the subnet group.
        subnet_ids (list): A list of subnet IDs to associate with the subnet group.

    Returns:
        dict: The response from the AWS API.
    """
    redshift_client = boto3.client('redshift')

    try:
        response = redshift_client.create_cluster_subnet_group(
            ClusterSubnetGroupName=subnet_group_name,
            SubnetIds=subnet_ids,
            Description=description,
        )
        print(f"Redshift Subnet Group '{subnet_group_name}' created successfully.")
        return response
    except redshift_client.exceptions.ClusterSubnetGroupAlreadyExistsFault:
        print(f"Subnet Group '{subnet_group_name}' already exists.")
    except Exception as e:
        print(f"An error occurred: {e}")



if __name__ == "__main__":
    pass
