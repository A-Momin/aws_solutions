import boto3, os, json
from datetime import date
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError

#==============================================================================
ec2_client = boto3.client('ec2', region_name='us-east-1')
ec2_resource = boto3.resource('ec2', region_name='us-east-1')
# region = os.environ['AWS_DEFAULT_REGION']
#==============================================================================

def create_vpc(cidr_block, tags=None):
    """
    Create an AWS VPC with specified options including subnets, internet gateway, route tables, and security groups.

    :param cidr_block: CIDR block for the VPC.
    :param subnet_configs: List of dictionaries with subnet configurations (CIDR block, AZ, etc.).
    :param create_igw: Boolean to determine if an Internet Gateway should be created. Default is True.
    :param route_table_configs: List of dictionaries with route table configurations. Default is None.
    :param security_group_configs: List of dictionaries with security group configurations. Default is None.
    :param tags: List of dictionaries with tags to apply to the resources.
    :raises ClientError: If there is an error creating the VPC or its components.
    :raises NoCredentialsError: If credentials are not available.
    :raises PartialCredentialsError: If incomplete credentials are provided.
    """
    try:

        # Create the VPC
        vpc = ec2_resource.create_vpc(CidrBlock=cidr_block)
        vpc.wait_until_available()
        print(f"VPC '{vpc.id}' created with CIDR block '{cidr_block}'")

        # Tag the VPC
        if tags:
            vpc.create_tags(Tags=tags)
            print(f"Tags {tags} applied to VPC '{vpc.id}'")
        
        return vpc

    except ClientError as e:
        print(f"Error creating VPC or its components: {e}")
        raise
    except NoCredentialsError:
        print("Credentials not available")
        raise
    except PartialCredentialsError:
        print("Incomplete credentials provided")
        raise

def dns_support(vpc_id):


    try:
        # Enable DNS support
        ec2_client.modify_vpc_attribute(VpcId=vpc_id, EnableDnsSupport={'Value': True})
        ec2_client.modify_vpc_attribute(VpcId=vpc_id, EnableDnsHostnames={'Value': True})
        print(f"DNS support enabled for VPC '{vpc_id}'")
    except ClientError as e:
        print(f"Error enablining DNS support or its components: {e}")
        raise
    except NoCredentialsError:
        print("Credentials not available")
        raise
    except PartialCredentialsError:
        print("Incomplete credentials provided")
        raise

def create_subnet(vpc_id, subnet_config, tags):

    try:
        # Create subnet
        subnet = ec2_resource.create_subnet(
            CidrBlock=subnet_config['cidr_block'],
            VpcId=vpc_id,
            AvailabilityZone=subnet_config['az']
        )
        print(f"Subnet '{subnet.id}' created with CIDR block '{subnet_config['cidr_block']}' in AZ '{subnet_config['az']}'")
        
        # Tag the subnet
        if tags:
            subnet.create_tags(Tags=tags)
            print(f"Tags {tags} applied to subnet '{subnet.id}'")
        
        return subnet.id

    except ClientError as e:
        print(f"Error creating Subnet or its components: {e}")
        raise
    except NoCredentialsError:
        print("Credentials not available")
        raise
    except PartialCredentialsError:
        print("Incomplete credentials provided")
        raise

def create_internet_gatway(vpc, tags):

    try:
        # Create Internet Gateway
        igw = ec2_resource.create_internet_gateway()

        # attach the IG with VPC
        vpc.attach_internet_gateway(InternetGatewayId=igw.id)
        print(f"Internet Gateway '{igw.id}' attached to VPC '{vpc.id}'")
        
        # Tag the Internet Gateway
        if tags:
            igw.create_tags(Tags=tags)
            print(f"Tags {tags} applied to Internet Gateway '{igw.id}'")
        
        return igw.id

    except ClientError as e:
        print(f"Error creating Internet Gateway or its components: {e}")
        raise
    except NoCredentialsError:
        print("Credentials not available")
        raise
    except PartialCredentialsError:
        print("Incomplete credentials provided")
        raise

def create_route_table(vpc_id, route_table_config, subnet_id, igw_id, tags):


    try:
        # Create route tables
        route_table = ec2_resource.create_route_table(VpcId=vpc_id)
        
        if 'routes' in route_table_config:
            for route in route_table_config['routes']:
                route_params = {'DestinationCidrBlock': route['destination_cidr_block']}
                
                if 'gateway_id' in route and route['gateway_id']: route_params['GatewayId'] = route['gateway_id']
                elif igw_id: route_params['GatewayId'] = igw_id
                
                if 'nat_gateway_id' in route and route['nat_gateway_id']:
                    route_params['NatGatewayId'] = route['nat_gateway_id']
                
                # Create a route within the Route Table
                route_table.create_route(**route_params)
        
        print(f"Route table '{route_table.id}' created for VPC '{vpc_id}'")
        
        # Tag the route table
        if tags:
            route_table.create_tags(Tags=tags)
            print(f"Tags {tags} applied to route table '{route_table.id}'")

        # Associate route table with subnets
        if subnet_id:
            route_table.associate_with_subnet(SubnetId=subnet_id)
            print(f"Route table '{route_table.id}' associated with subnet '{subnet_id}'")

    except ClientError as e:
        print(f"Error creating Route Table or its components: {e}")
        raise
    except NoCredentialsError:
        print("Credentials not available")
        raise
    except PartialCredentialsError:
        print("Incomplete credentials provided")
        raise

def create_security_group(vpc_id, security_group_configs, tags):


    try:
        # Create security groups if specified
        if security_group_configs:
            for sg_config in security_group_configs:
                security_group = ec2_resource.create_security_group(
                    GroupName=sg_config['group_name'],
                    Description=sg_config['description'],
                    VpcId=vpc_id
                )
                if 'ingress_rules' in sg_config:
                    for rule in sg_config['ingress_rules']:
                        security_group.authorize_ingress(
                            IpProtocol=rule['protocol'],
                            CidrIp=rule['cidr_ip'],
                            FromPort=rule['from_port'],
                            ToPort=rule['to_port']
                        )
                if 'egress_rules' in sg_config:
                    for rule in sg_config['egress_rules']:
                        security_group.authorize_egress(
                            IpPermissions=[{
                                'IpProtocol': rule['protocol'],
                                'IpRanges': [{'CidrIp': rule['cidr_ip']}],
                                'FromPort': rule['from_port'],
                                'ToPort': rule['to_port']
                            }]
                        )
                print(f"Security group '{security_group.id}' created with name '{sg_config['group_name']}'")
                
                # Tag the security group
                if tags:
                    security_group.create_tags(Tags=tags)
                    print(f"Tags {tags} applied to security group '{security_group.id}'")

    except ClientError as e:
        print(f"Error creating security group or its components: {e}")
        raise
    except NoCredentialsError:
        print("Credentials not available")
        raise
    except PartialCredentialsError:
        print("Incomplete credentials provided")
        raise

def delete_vpc_with_dependencies(vpc_id):
    """
    Delete an AWS VPC along with all its dependencies given the VPC ID.

    :param vpc_id: ID of the VPC to delete.
    :return: True if VPC and its dependencies are deleted successfully, False otherwise.
    """

    try:
        # Get the VPC
        vpc = ec2_resource.Vpc(vpc_id)

        # Detach and delete all internet gateways
        for igw in vpc.internet_gateways.all():
            vpc.detach_internet_gateway(InternetGatewayId=igw.id)
            # Delete the Internet Gateway
            igw.delete()
            # ec2_client.delete_internet_gateway(InternetGatewayId=igw.id)
            print(f"Deleted Internet Gateway: {igw.id}")

        # Delete all route table associations and route tables
        for rt in vpc.route_tables.all():
            for association in rt.associations:
                if not association.main:
                    ec2_client.disassociate_route_table(AssociationId=association.id)
            if not rt.associations_attribute or all(not assoc['Main'] for assoc in rt.associations_attribute):
                rt.delete()
                print(f"Deleted Route Table: {rt.id}")

        # Delete all network ACLs (except the default one)
        for acl in vpc.network_acls.all():
            if not acl.is_default:
                acl.delete()
                print(f"Deleted Network ACL: {acl.id}")

        # Delete all subnets
        for subnet in vpc.subnets.all():
            for eni in subnet.network_interfaces.all():
                eni.delete()
                print(f"Deleted Network Interface: {eni.id}")
            subnet.delete()
            print(f"Deleted Subnet: {subnet.id}")

        # Delete all security groups (except the default one)
        for sg in vpc.security_groups.all():
            if sg.group_name != 'default':
                sg.delete()
                print(f"Deleted Security Group: {sg.id}")

        # Finally, delete the VPC
        vpc.delete()
        print(f"Deleted VPC: {vpc_id}")

        return True

    except ClientError as e:
        print(f"An error occurred: {e}")
        return False

def serialize_security_group():
    def _serialize_security_group(security_group_id, file_path):
        """
        Fetch and serialize the details of an AWS security group given its ID.

        :param security_group_id: The ID of the security group to serialize.
        :return: JSON string of the security group details.
        :raises Exception: If there is an error fetching or serializing the security group.
        """
        ec2_client = boto3.client('ec2')

        try:
            response = ec2_client.describe_security_groups(GroupIds=[security_group_id])
            security_group = response['SecurityGroups'][0]  # Assuming the ID is unique and we get only one SG
            
            security_group_json = json.dumps(security_group, indent=4)
            
            # Write the JSON string to a file
            with open(file_path, 'w') as json_file:
                json_file.write(security_group_json)
            
            print(f"Security group details saved to {file_path}")
                
            return security_group_json

        except NoCredentialsError:
            print("Credentials not available")
            raise
        except PartialCredentialsError:
            print("Incomplete credentials provided")
            raise
        except ClientError as e:
            print(f"An error occurred: {e}")
            raise

    security_group_id = 'sg-07f4ccd7a5be677ea'  # Replace with your security group ID
    file_path = 'serialized_aws_sg.json'  # Replace with your desired file path
    try:
        _serialize_security_group(security_group_id, file_path)
    except Exception as e:
        print(f"Failed to serialize security group: {e}")

def create_public_subnet():
    def _create_public_subnet(vpc_id, cidr_block, availability_zone, region):
        """
        Create a public subnet in the specified VPC.

        :param vpc_id: The ID of the VPC.
        :param cidr_block: The CIDR block for the subnet.
        :param availability_zone: The availability zone for the subnet.
        :param region: The AWS region where the subnet will be created.
        :return: The ID of the created subnet.
        """
        ec2 = boto3.resource('ec2', region_name=region)
        ec2_client = boto3.client('ec2', region_name=region)

        try:
            # Create the subnet
            subnet = ec2.create_subnet(CidrBlock=cidr_block, VpcId=vpc_id, AvailabilityZone=availability_zone)
            print(f"Created subnet {subnet.id} in VPC {vpc_id}")

            # Create an internet gateway
            igw = ec2.create_internet_gateway()
            print(f"Created internet gateway {igw.id}")

            # Attach the internet gateway to the VPC
            vpc = ec2.Vpc(vpc_id)
            vpc.attach_internet_gateway(InternetGatewayId=igw.id)
            print(f"Attached internet gateway {igw.id} to VPC {vpc_id}")

            # Create a route table
            route_table = vpc.create_route_table()
            print(f"Created route table {route_table.id}")

            # Create a route to the internet gateway
            route_table.create_route(DestinationCidrBlock='0.0.0.0/0', GatewayId=igw.id)
            print(f"Created route to IGW {igw.id} in route table {route_table.id}")

            # Associate the route table with the subnet
            route_table.associate_with_subnet(SubnetId=subnet.id)
            print(f"Associated route table {route_table.id} with subnet {subnet.id}")

            # Modify the subnet attribute to enable auto-assign public IP
            ec2_client.modify_subnet_attribute(SubnetId=subnet.id, MapPublicIpOnLaunch={'Value': True})
            print(f"Enabled auto-assign public IP for subnet {subnet.id}")

            return subnet.id

        except NoCredentialsError:
            print("Credentials not available")
            raise
        except PartialCredentialsError:
            print("Incomplete credentials provided")
            raise
        except ClientError as e:
            print(f"An error occurred: {e}")
            raise

    # Example usage
    vpc_id = 'vpc-0123456789abcdef0'  # Replace with your VPC ID
    cidr_block = '10.0.1.0/24'  # Replace with your desired CIDR block
    availability_zone = 'us-east-1a'  # Replace with your desired availability zone
    region = 'us-east-1'  # Replace with your desired AWS region

    try:
        subnet_id = _create_public_subnet(vpc_id, cidr_block, availability_zone, region)
        print(f"Successfully created public subnet with ID: {subnet_id}")
    except Exception as e:
        print(f"Failed to create public subnet: {e}")

def create_vpc_with_options():
    try:
        # 1. Create a VPC
        vpc_response = ec2_client.create_vpc(
            CidrBlock='10.0.0.0/16',  # Define the CIDR block for the VPC
            TagSpecifications=[
                {
                    'ResourceType': 'vpc',
                    'Tags': [{'Key': 'Name', 'Value': 'MyVPC'}]
                }
            ]
        )
        vpc_id = vpc_response['Vpc']['VpcId']
        print(f"VPC created: {vpc_id}")

        # Enable DNS support and DNS hostnames
        ec2_client.modify_vpc_attribute(VpcId=vpc_id, EnableDnsSupport={'Value': True})
        ec2_client.modify_vpc_attribute(VpcId=vpc_id, EnableDnsHostnames={'Value': True})

        # 2. Create an Internet Gateway (IGW) and attach it to the VPC
        igw_response = ec2_client.create_internet_gateway(
            TagSpecifications=[
                {
                    'ResourceType': 'internet-gateway',
                    'Tags': [{'Key': 'Name', 'Value': 'MyIGW'}]
                }
            ]
        )
        igw_id = igw_response['InternetGateway']['InternetGatewayId']
        ec2_client.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
        print(f"Internet Gateway created and attached: {igw_id}")

        # 3. Create Subnets
        public_subnet_response = ec2_client.create_subnet(
            CidrBlock='10.0.1.0/24',
            VpcId=vpc_id,
            AvailabilityZone='us-east-1a',
            TagSpecifications=[
                {
                    'ResourceType': 'subnet',
                    'Tags': [{'Key': 'Name', 'Value': 'PublicSubnet'}]
                }
            ]
        )
        public_subnet_id = public_subnet_response['Subnet']['SubnetId']
        print(f"Public Subnet created: {public_subnet_id}")

        private_subnet_response = ec2_client.create_subnet(
            CidrBlock='10.0.2.0/24',
            VpcId=vpc_id,
            AvailabilityZone='us-east-1b',
            TagSpecifications=[
                {
                    'ResourceType': 'subnet',
                    'Tags': [{'Key': 'Name', 'Value': 'PrivateSubnet'}]
                }
            ]
        )
        private_subnet_id = private_subnet_response['Subnet']['SubnetId']
        print(f"Private Subnet created: {private_subnet_id}")

        # 4. Create a Route Table for Public Subnet and associate it
        route_table_response = ec2_client.create_route_table(
            VpcId=vpc_id,
            TagSpecifications=[
                {
                    'ResourceType': 'route-table',
                    'Tags': [{'Key': 'Name', 'Value': 'PublicRouteTable'}]
                }
            ]
        )
        route_table_id = route_table_response['RouteTable']['RouteTableId']
        print(f"Route Table created: {route_table_id}")

        # Create a public route to the Internet
        ec2_client.create_route(
            RouteTableId=route_table_id,
            DestinationCidrBlock='0.0.0.0/0',
            GatewayId=igw_id
        )
        # Associate the route table with the public subnet
        ec2_client.associate_route_table(RouteTableId=route_table_id, SubnetId=public_subnet_id)
        print("Route Table associated with Public Subnet")

        # 5. Modify Public Subnet to enable auto-assign public IP
        ec2_client.modify_subnet_attribute(SubnetId=public_subnet_id, MapPublicIpOnLaunch={'Value': True})

        # 6. Create a NAT Gateway for Private Subnet (Requires an Elastic IP)
        eip_response = ec2_client.allocate_address(Domain='vpc')
        allocation_id = eip_response['AllocationId']

        nat_gateway_response = ec2_client.create_nat_gateway(
            SubnetId=public_subnet_id,
            AllocationId=allocation_id,
            TagSpecifications=[
                {
                    'ResourceType': 'natgateway',
                    'Tags': [{'Key': 'Name', 'Value': 'MyNATGateway'}]
                }
            ]
        )
        nat_gateway_id = nat_gateway_response['NatGateway']['NatGatewayId']
        print(f"NAT Gateway created: {nat_gateway_id}")

        # Wait for the NAT Gateway to become available
        waiter = ec2_client.get_waiter('nat_gateway_available')
        waiter.wait(NatGatewayIds=[nat_gateway_id])
        print("NAT Gateway is now available")

        # 7. Create a Route Table for Private Subnet and associate it
        private_route_table_response = ec2_client.create_route_table(
            VpcId=vpc_id,
            TagSpecifications=[
                {
                    'ResourceType': 'route-table',
                    'Tags': [{'Key': 'Name', 'Value': 'PrivateRouteTable'}]
                }
            ]
        )
        private_route_table_id = private_route_table_response['RouteTable']['RouteTableId']
        print(f"Private Route Table created: {private_route_table_id}")

        # Create a route in the private route table to the NAT Gateway
        ec2_client.create_route(
            RouteTableId=private_route_table_id,
            DestinationCidrBlock='0.0.0.0/0',
            NatGatewayId=nat_gateway_id
        )
        # Associate the private route table with the private subnet
        ec2_client.associate_route_table(RouteTableId=private_route_table_id, SubnetId=private_subnet_id)
        print("Private Route Table associated with Private Subnet")

        print("VPC and all related resources created successfully!")
    except Exception as e:
        print(f"Error creating VPC: {e}")


if __name__ == "__main__":
    # Example usage
    cidr_block = '10.0.0.0/16'
    region = 'us-east-1'  # Specify the AWS region, e.g., 'us-east-1'

    subnet_configs = [
        {'cidr_block': '10.0.1.0/24', 'az': 'us-east-1a'},
        {'cidr_block': '10.0.2.0/24', 'az': 'us-east-1b'}
    ]

    route_table_configs = [
        {
            'routes': [
                {'destination_cidr_block': '0.0.0.0/0'}  # Will be replaced with IGW ID if create_igw=True
            ]
        }
    ]

    security_group_configs = [
        {
            'group_name': f"EMR-{date.today().strftime('%Y-%m-%d')}-sg",
            'description': f"EMR-{date.today().strftime('%Y-%m-%d')} security group",
            'ingress_rules': [
                {'protocol': 'tcp', 'cidr_ip': '0.0.0.0/0', 'from_port': 80, 'to_port': 80},
                {'protocol': 'tcp', 'cidr_ip': '0.0.0.0/0', 'from_port': 443, 'to_port': 443}
            ],
            'egress_rules': [
                {'protocol': 'tcp', 'cidr_ip': '0.0.0.0/0', 'from_port': 0, 'to_port': 0}
            ]
        }
    ]

    tags = [
        {'Key': 'Name', 'Value': 'EMR-Cluster-' + date.today().strftime('%Y-%m-%d')},
        {'Key': 'Environment', 'Value': 'Test'}
    ]

    # vpc = create_vpc(cidr_block, region, tags)
    
    # # Create Internet Gateway and attach that with VPC
    # igw_id = create_internet_gatway(vpc, region, tags)

    # for subnet_config in subnet_configs:
    #     subnet_id = create_subnet(vpc.id, subnet_config, region, tags)
    #     create_route_table(vpc.id, route_table_configs[0], subnet_id, igw_id, region, tags)


    # delete_vpc_with_dependencies(vpc_id)
