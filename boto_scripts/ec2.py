import boto3, botocore
from botocore.exceptions import ClientError
import os, time, json, io, zipfile
from datetime import date
from dotenv import load_dotenv

#==============================================================================
ALL_IN_ONE_SG = ''
ACCOUNT_ID        = os.environ['AWS_ACCOUNT_ID_ROOT']
REGION            = os.environ['AWS_DEFAULT_REGION']
VPC_ID            = os.environ['AWS_DEFAULT_VPC']
SECURITY_GROUP_ID = os.environ['AWS_DEFAULT_SG_ID']
SUBNET_IDS        = SUBNET_IDS = os.environ["AWS_DEFAULT_SUBNET_IDS"].split(":")
SUBNET_ID         = SUBNET_IDS[0]
AWS_DEFAULT_IMAGE_ID      = os.environ['AWS_DEFAULT_IMAGE_ID']
AWS_DEFAULT_INSTANCE_TYPE = os.environ['AWS_DEFAULT_INSTANCE_TYPE']
AWS_DEFAULT_KEY_PAIR_NAME = os.environ['AWS_DEFAULT_KEY_PAIR_NAME']

ec2_client           = boto3.client('ec2', region_name=REGION)
ec2_resource         = boto3.resource('ec2', region_name=REGION)
#==============================================================================

# Example usage
ALL_IN_ONE_INBOUND_RULES = [
    {
        'IpProtocol': 'tcp',
        'FromPort': 22,
        'ToPort': 22,
        'IpRanges': [{'CidrIp': '0.0.0.0/0', "Description": "SSH_Port"}]
    },
    {
        'IpProtocol': 'tcp',
        'FromPort': 80,
        'ToPort': 80,
        'IpRanges': [{'CidrIp': '0.0.0.0/0', "Description": "HTTP_Port"}]
    },
    {
        'IpProtocol': 'tcp',
        'FromPort': 443,
        'ToPort': 443,
        'IpRanges': [{'CidrIp': '0.0.0.0/0', "Description": "HTTPs_Port"}]
    },
    {
        'IpProtocol': 'tcp',
        'FromPort': 8000,
        'ToPort': 8000,
        'IpRanges': [{'CidrIp': '0.0.0.0/0', "Description": "Django_Port1"}]
    },
    {
        'IpProtocol': 'tcp',
        'FromPort': 8010,
        'ToPort': 8010,
        'IpRanges': [{'CidrIp': '0.0.0.0/0', "Description": "Django_Port2"}]
    },
    {
        'IpProtocol': 'tcp',
        'FromPort': 8080,
        'ToPort': 8080,
        'IpRanges': [{'CidrIp': '0.0.0.0/0', "Description": "Jenkins_Port"}]
    },
    {
        'IpProtocol': 'tcp',
        'FromPort': 8888,
        'ToPort': 8888,
        'IpRanges': [{'CidrIp': '0.0.0.0/0', "Description": "JupyterNotebook_Port"}]
    },
    {
        'IpProtocol': 'tcp',
        'FromPort': 3306,
        'ToPort': 3306,
        'IpRanges': [{'CidrIp': '0.0.0.0/0', "Description": "AWS_RDS_MySQL_Port"}]
    },
    {
        'IpProtocol': 'tcp',
        'FromPort': 4243,
        'ToPort': 4243,
        'IpRanges': [{'CidrIp': '0.0.0.0/0', "Description": "docker_host"}]
    },
    {
        'IpProtocol': 'tcp',
        'FromPort': 32768,
        'ToPort': 60999,
        'IpRanges': [{'CidrIp': '0.0.0.0/0', "Description": "docker_host_communication"}]
    },
]

ALL_IN_ONE_OUTBOUND_RULES = [
    {
        'IpProtocol': '-1', # '-1' means all protocols
        'FromPort': -1,
        'ToPort': -1,
        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
    }
]

tags = [
    {
        'Key': 'Name',
        'Value': 'ALL_IN_ONE_SG'
    }
]



def create_security_group(
        group_name,
        vpc_id,
        inbound_rules=ALL_IN_ONE_INBOUND_RULES,
        outbound_rules=ALL_IN_ONE_OUTBOUND_RULES,
        tags=tags,
        description: str = 'All in one useful security groups roles'
    ):
    """
    Creates an AWS security group with optional inbound and outbound rules and tags.

    Parameters:
    group_name (str): The name of the security group.
    vpc_id (str): The ID of the VPC where the security group will be created.
    inbound_rules (list, optional): A list of dictionaries defining inbound rules.
    outbound_rules (list, optional): A list of dictionaries defining outbound rules.
    tags (list, optional): A list of dictionaries defining tags.

    Returns:
    dict: Information about the created security group, including the group ID.
    """

    try:
        # Create the security group
        response = ec2_client.create_security_group(
            GroupName=group_name,
            Description=description,
            VpcId=vpc_id
        )
        security_group_id = response['GroupId']
        print(f"Security Group '{security_group_id}' is Created in VPC {vpc_id}")

        # Add inbound rules if provided
        if inbound_rules:
            ec2_client.authorize_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions=inbound_rules
            )

            # Adds an inbound rule to allow all traffic from instances within the same security group.
            ec2_client.authorize_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions=[
                    {
                        'IpProtocol': '-1',  # '-1' means all protocols
                        'UserIdGroupPairs': [
                            {
                                'GroupId': security_group_id,
                                'Description': 'Allow all traffic from the same security group'
                            }
                        ]
                    }
                ]
            )

        # Check existing outbound rules
        existing_sg = ec2_client.describe_security_groups(GroupIds=[security_group_id])
        existing_outbound_rules = existing_sg['SecurityGroups'][0]['IpPermissionsEgress']

        # Add outbound rules if they don't already exist
        if outbound_rules:
            for rule in outbound_rules:
                if rule not in existing_outbound_rules:
                    try:
                        ec2_client.authorize_security_group_egress(
                            GroupId=security_group_id,
                            IpPermissions=[rule]
                        )
                    except ClientError as e:
                        print(f"Error adding outbound rule: {e}")
                        continue

        # Add tags if provided
        if tags:
            ec2_client.create_tags(
                Resources=[security_group_id],
                Tags=tags
            )

        return response

    except ClientError as e:
        print(f"Error: {e}")
        return None


def allow_sg_to_sg(this_security_group_id, source_security_group_id='', ip_protocol='tcp', from_port=80, to_port=80):
    """
    Adds an inbound rule to allow all traffic from same/different secutity group.

    Parameters:
    security_group_id (str): The ID of the security group.

    Returns:
    dict: The response from the AWS EC2 client.
    """
    
    try:
        response = ec2_client.authorize_security_group_ingress(
            GroupId=this_security_group_id,
            IpPermissions=[
                {
                    'IpProtocol': ip_protocol if ip_protocol else '-1',  # '-1' means all protocols
                    'FromPort': from_port,
                    'ToPort': to_port,
                    'UserIdGroupPairs': [
                        {
                            'GroupId': source_security_group_id if source_security_group_id else this_security_group_id,
                            'Description': 'Allow all traffic from the same/different security group'
                        }
                    ]
                }
            ]
        )
        return response

    except ClientError as e:
        print(f"Error: {e}")
        return None

def remove_all_rules(security_group_id):
    try:
        # Get the current rules of the security group
        response = ec2_client.describe_security_groups(GroupIds=[security_group_id])
        security_group = response['SecurityGroups'][0]
        
        # Remove all inbound (ingress) rules
        ingress_rules = security_group.get('IpPermissions', [])
        if ingress_rules:
            ec2_client.revoke_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions=ingress_rules
            )
            print(f"Removed all inbound rules from Security Group: {security_group_id}")
        
        # Remove all outbound (egress) rules
        egress_rules = security_group.get('IpPermissionsEgress', [])
        if egress_rules:
            ec2_client.revoke_security_group_egress(
                GroupId=security_group_id,
                IpPermissions=egress_rules
            )
            print(f"Removed all outbound rules from Security Group: {security_group_id}")
    
    except Exception as e:
        print(f"Error removing rules from Security Group: {security_group_id}. Error: {str(e)}")

def remove_all_ingress_rules(security_group_id):
    try:
        # Describe the security group to get all ingress rules
        response = ec2_client.describe_security_groups(GroupIds=[security_group_id])
        security_group = response['SecurityGroups'][0]

        # Extract all ingress rules
        ip_permissions = security_group['IpPermissions']

        # Revoke all ingress rules
        if ip_permissions:
            ec2_client.revoke_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions=ip_permissions
            )
            print(f"Successfully removed all ingress rules from Security Group {security_group_id}")
        else:
            print(f"No ingress rules to remove for Security Group {security_group_id}")
    except ClientError as e:
        print(f"Error removing ingress rules: {e}")

def delete_security_group(security_group_id):
    try: 
        # Check for associated ENIs
        filters = [{'Name': 'group-id', 'Values': [security_group_id]}]
        enis = ec2_client.describe_network_interfaces(Filters=filters)['NetworkInterfaces']

        for eni in enis:
            eni_id = eni['NetworkInterfaceId']
            print(f"Detaching Security Group from ENI: {eni_id}")
            ec2_client.modify_network_interface_attribute(
                NetworkInterfaceId=eni_id,
                Groups=[group['GroupId'] for group in eni['Groups'] if group['GroupId'] != security_group_id]
            )
        
        # Check for EC2 instances using the security group
        instances = ec2_client.describe_instances(
            Filters=[{'Name': 'instance.group-id', 'Values': [security_group_id]}]
        )['Reservations']
        
        for reservation in instances:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                print(f"Detaching Security Group from Instance: {instance_id}")
                ec2_client.modify_instance_attribute(
                    InstanceId=instance_id,
                    Groups=[group['GroupId'] for group in instance['SecurityGroups'] if group['GroupId'] != security_group_id]
                )

        # Finally, delete the security group
        ec2_client.delete_security_group(GroupId=security_group_id)
        print(f"Deleted Security Group: {security_group_id}")

    except ClientError as e:
        print(f"Error: {e}")


def run_ec2_instance(
    image_id=AWS_DEFAULT_IMAGE_ID, 
    instance_type=AWS_DEFAULT_INSTANCE_TYPE, 
    key_pair_name=AWS_DEFAULT_KEY_PAIR_NAME, 
    tag_name="BASIC_EC2", 
    volume_size=8, 
    security_group_ids=[ALL_IN_ONE_SG]
    ):
    """
    Launches an EC2 instance with specified parameters and tagging.

    Args:
        image_id (str): AMI ID to use for the instance.
        instance_type (str): EC2 instance type (e.g., 't2.micro').
        key_pair_name (str): Name of the key pair.
        tag_name (str): Name tag for the instance.
        volume_size (int): Size of the EBS volume in GiB. Default is 8 GiB.
        security_group_ids (list): List of security group IDs. Default is None.
        subnet_id (str): Subnet ID for the instance. Default is None.

    Returns:
        str: The ID of the launched instance.
    """
    ec2_client = boto3.client('ec2')

    try:
        response = ec2_client.run_instances(
            ImageId=image_id,
            InstanceType=instance_type,
            MinCount=1,
            MaxCount=1,
            KeyName=key_pair_name,
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [{'Key': 'Name', 'Value': tag_name}]
                }
            ],
            BlockDeviceMappings=[
                {
                    'DeviceName': '/dev/xvda',  # Default root volume
                    'Ebs': {
                        'VolumeSize': volume_size,  # Volume size in GiB
                        'VolumeType': 'gp2'        # General Purpose SSD
                    }
                }
            ],
            SecurityGroupIds=security_group_ids if security_group_ids else [],
        )

        instance_id = response['Instances'][0]['InstanceId']
        print(f"Instance created with ID: {instance_id}")
        return instance_id

    except Exception as e:
        print(f"Failed to launch EC2 instance: {e}")
        raise


def remove_route_with_prefix_list(route_table_id, prefix_list_id):
    """
    Remove a route from the Route Table based on a VPC Endpoint (Prefix List).
    
    :param route_table_id: The ID of the Route Table.
    :param prefix_list_id: The ID of the Prefix List associated with the VPC Endpoint.
    """
    ec2_client = boto3.client('ec2')
    
    try:
        # Delete the route with a prefix list ID
        response = ec2_client.delete_route(
            RouteTableId=route_table_id,
            DestinationPrefixListId=prefix_list_id
        )
        
        print(f"Route with Prefix List {prefix_list_id} removed from Route Table {route_table_id}.")
        return response
    
    except ec2_client.exceptions.ClientError as e:
        print(f"Error: {e}")
        return None

def run_ec2_instance_v2(
    image_id: str,
    instance_type: str,
    key_name: str,
    security_group_ids: list,
    subnet_id: str,
    min_count: int = 1,
    max_count: int = 1,
    block_device_mappings: list = None,
    user_data: str = None,
    iam_instance_profile: dict = None,
    tags: list = None,
    monitoring: bool = False,
    disable_api_termination: bool = False,
    instance_initiated_shutdown_behavior: str = "stop",
    private_ip_address: str = None
    ):
    """
    Creates and runs an AWS EC2 instance with specified parameters.
    
    Parameters:
        image_id (str): The ID of the AMI to use.
        instance_type (str): The type of instance (e.g., 't2.micro').
        key_name (str): The name of the key pair for SSH access.
        security_group_ids (list): List of security group IDs.
        subnet_id (str): The ID of the subnet to launch the instance in.
        min_count (int): Minimum number of instances to launch.
        max_count (int): Maximum number of instances to launch.
        block_device_mappings (list): List of block device mapping dictionaries.
        user_data (str): User data script for the instance.
        iam_instance_profile (dict): IAM role to associate with the instance.
        tags (list): List of tag dictionaries for the instance.
        monitoring (bool): Enable detailed monitoring (default is False).
        disable_api_termination (bool): Prevent instance termination via API.
        instance_initiated_shutdown_behavior (str): 'stop' or 'terminate' on shutdown.
        private_ip_address (str): Private IP address to assign.
    
    Returns:
        dict: Details of the created instances.
    """
    ec2_client = boto3.client("ec2")
    
    try:
        # Create EC2 instance
        response = ec2_client.run_instances(
            ImageId=image_id,
            InstanceType=instance_type,
            KeyName=key_name,
            SecurityGroupIds=security_group_ids,
            SubnetId=subnet_id,
            MinCount=min_count,
            MaxCount=max_count,
            BlockDeviceMappings=block_device_mappings,
            UserData=user_data,
            IamInstanceProfile=iam_instance_profile,
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': tags or []
                }
            ] if tags else None,
            Monitoring={'Enabled': monitoring},
            DisableApiTermination=disable_api_termination,
            InstanceInitiatedShutdownBehavior=instance_initiated_shutdown_behavior,
            PrivateIpAddress=private_ip_address
        )
        return response
    except Exception as e:
        print(f"Error creating EC2 instance: {e}")
        return None


def create_vpc_endpoint():

    # VPC Endpoint parameters
    VPC_ENDPOINT_TAG = 'rds-vpc-endpoint' + date.today().strftime('%Y%m%d')
    VPC_ENDPOINT_SERVICE_NAME = f"com.amazonaws.{REGION}.s3"
    SECURITY_GROUP_IDS = [SECURITY_GROUP_ID]  # Security group(s) associated with the endpoint
    ROUTE_TABLE_IDS = ['rtb-0ec4311296ec952f8']

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


if __name__ == "__main__":
    response = run_ec2_instance_v2(
        image_id="ami-12345678",  # Replace with a valid AMI ID
        instance_type="t3.medium",
        key_name="AMominNJ",  # Replace with your key pair name
        security_group_ids=[ALL_IN_ONE_SG],
        # subnet_id="subnet-123abc45",  # Replace with a valid subnet ID
        min_count=1,
        max_count=1,
        block_device_mappings=[
            {
                "DeviceName": "/dev/xvda",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "VolumeSize": 20,
                    "VolumeType": "gp3"
                }
            }
        ],
        # user_data="""#!/bin/bash
        #              echo "Hello, World!" > /var/www/html/index.html""",
        iam_instance_profile={
            "Name": "EC2InstanceRole"  # Replace with an existing IAM role name
        },
        tags=[
            {"Key": "Name", "Value": "MyEC2Instance"},
            {"Key": "Environment", "Value": "Development"}
        ],
        monitoring=True,
        disable_api_termination=True,
        instance_initiated_shutdown_behavior="terminate",
        private_ip_address="10.0.1.100"
    )
    print(response)

