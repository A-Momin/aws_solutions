
# [Boto3 IAM Doc](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html)

import boto3
import botocore
from botocore.exceptions import ClientError
import os, time, json
from dotenv import load_dotenv
from misc import load_from_yaml, save_to_yaml

## ============================================================================

# Initialize boto3 clients
iam_client = boto3.client('iam')
lfn_client = boto3.client("lambda")
lambda_client = boto3.client('lambda', region_name=os.environ['AWS_DEFAULT_REGION'])

account_id = os.environ['AWS_ACCOUNT_ID_ROOT']
region = os.environ['AWS_DEFAULT_REGION']
PASSWORD = os.environ['PASSWORD']
## ============================================================================

ASSUME_ROLE_POLICY_DOC = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": f"service_name.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}


# 1. Create IAM Roles and Policies
def create_iam_role(role_name, policy_document, description=""):
    try:
        response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(policy_document),
            Description=description
        )
        return response['Role']['Arn']
    except iam_client.exceptions.EntityAlreadyExistsException:
        print(f"Role {role_name} already exists.")
        return iam_client.get_role(RoleName=role_name)['Role']['Arn']

def put_inline_role_policy(role_name: str, policy_name: str, policy_document=None):
    """
    Attaches an INLINE policy to the specified IAM role.

    Parameters:
    role_name (str): The name of the IAM role to attach the policy to.
    policy_name (str): The name of the policy to attach.
    policy_document (dict, optional): The policy document (in JSON format) to attach.
                                       If not provided, a default S3 access policy will be used.

    Example:
    put_inline_role_policy('example-role', 'example-policy')

    """
    # Define the policy document (JSON)
    default_policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    "arn:aws:s3:::example-bucket",
                    "arn:aws:s3:::example-bucket/*"
                ]
            }
        ]
    }
    
    policy_document = policy_document or default_policy_document


    try:
        # Attach the inline policy to the role
        response = iam_client.put_role_policy(
            RoleName=role_name,
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document)
        )
        print(f"Inline policy '{policy_name}' successfully attached to role '{role_name}'.")
    except ClientError as e:
        print(f"Error: {e}")

def create_customer_managed_policy(policy_name, policy_document, description):
    try:
        response = iam_client.create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document),
            Description=description
        )
        return response
    except iam_client.exceptions.EntityAlreadyExistsException:
        return f"Policy {policy_name} already exists."
    except Exception as e:
        return f"Error creating policy: {e}"

def attach_policy_to_role(role_name, policy_arn):
    try:
        response = iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_arn
        )
        return response
    except Exception as e:
        return f"Error attaching policy: {e}"

def delete_iam_role(role_name):
    """
    Deletes an IAM role and detaches all attached policies.

    Args:
        role_name (str): The name of the IAM role to delete.
    """

    try:
        # Detach all policies attached to the role
        attached_policies = iam_client.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']
        for policy in attached_policies:
            iam_client.detach_role_policy(RoleName=role_name, PolicyArn=policy['PolicyArn'])
            print(f"Detached policy {policy['PolicyArn']} from role {role_name}")

        # Remove all inline policies
        inline_policies = iam_client.list_role_policies(RoleName=role_name)['PolicyNames']
        for policy_name in inline_policies:
            iam_client.delete_role_policy(RoleName=role_name, PolicyName=policy_name)
            print(f"Deleted inline policy {policy_name} from role {role_name}")

        # Delete the role
        iam_client.delete_role(RoleName=role_name)
        print(f"Deleted role {role_name}")

    except botocore.exceptions.ClientError as error:
        print(f"Error deleting role {role_name}: {error}")

def delete_iam_policy(policy_arn):

    try:
        # Detach the policy from all roles
        roles = iam_client.list_entities_for_policy(PolicyArn=policy_arn, EntityFilter='Role')
        for role in roles['PolicyRoles']:
            iam_client.detach_role_policy(
                RoleName=role['RoleName'],
                PolicyArn=policy_arn
            )
            print(f"Detached policy from role: {role['RoleName']}")

        # Detach the policy from all users
        users = iam_client.list_entities_for_policy(PolicyArn=policy_arn, EntityFilter='User')
        for user in users['PolicyUsers']:
            iam_client.detach_user_policy(
                UserName=user['UserName'],
                PolicyArn=policy_arn
            )
            print(f"Detached policy from user: {user['UserName']}")

        # Detach the policy from all groups
        groups = iam_client.list_entities_for_policy(PolicyArn=policy_arn, EntityFilter='Group')
        for group in groups['PolicyGroups']:
            iam_client.detach_group_policy(
                GroupName=group['GroupName'],
                PolicyArn=policy_arn
            )
            print(f"Detached policy from group: {group['GroupName']}")

        # List and delete all versions of the policy
        versions = iam_client.list_policy_versions(PolicyArn=policy_arn)
        for version in versions['Versions']:
            if version['IsDefaultVersion']:
                continue
            iam_client.delete_policy_version(
                PolicyArn=policy_arn,
                VersionId=version['VersionId']
            )
            print(f"Deleted policy version: {version['VersionId']}")

        # Delete the policy
        iam_client.delete_policy(PolicyArn=policy_arn)
        print(f"Successfully deleted policy: {policy_arn}")

    except ClientError as e:
        print(f"ClientError: {e}")
    except Exception as e:
        print(f"Error: {e}")

def create_iam_user(user_name, password=PASSWORD, group_name='', policy_name='', mfa_device_name=''):

    # Step 1: Create the IAM User
    try:
        user_response = iam_client.create_user(UserName=user_name)
        print(f"User created: {user_response['User']['UserName']}")
    except iam_client.exceptions.EntityAlreadyExistsException:
        print(f"User {user_name} already exists.")

    # Step 2: Create the User’s Login Profile (for Console Access)
    try:
        login_profile_response = iam_client.create_login_profile(
            UserName=user_name,
            Password=password,
            PasswordResetRequired=False  # User will not be required to change password at next login
        )
        print(f"Login profile created for user {user_name}")
    except iam_client.exceptions.EntityAlreadyExistsException:
        print(f"Login profile for {user_name} already exists.")

    # Step 3: Create Access Keys (for Programmatic Access)
    access_key_response = iam_client.create_access_key(UserName=user_name)
    access_key_id = access_key_response['AccessKey']['AccessKeyId']
    secret_access_key = access_key_response['AccessKey']['SecretAccessKey']

    print(f"Access Key ID: {access_key_id}")
    print(f"Secret Access Key: {secret_access_key}")

    # Step 4: Attach a Managed Policy (e.g., AmazonS3ReadOnlyAccess)
    managed_policy_arn = 'arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess'

    iam_client.attach_user_policy(UserName=user_name, PolicyArn=managed_policy_arn)
    print(f"Managed policy {managed_policy_arn} attached to user {user_name}")

    # Step 5: Create and Attach Inline Policy
    inline_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "s3:*",
                "Resource": "*"
            }
        ]
    }

    if policy_name:
        iam_client.put_user_policy(
            UserName=user_name,
            PolicyName=policy_name,
            PolicyDocument=json.dumps(inline_policy)
        )
        print(f"Inline policy {policy_name} attached to user {user_name}")

    # Step 6: Add User to a Group
    if group_name:
        try:
            iam_client.create_group(GroupName=group_name)
            print(f"Group {group_name} created.")
        except iam_client.exceptions.EntityAlreadyExistsException:
            print(f"Group {group_name} already exists.")

        iam_client.add_user_to_group(GroupName=group_name, UserName=user_name)
        print(f"User {user_name} added to group {group_name}")

    # Step 7: Enable MFA (Virtual MFA Device)
    # Step 7.1: Create a virtual MFA device
    if mfa_device_name:
        mfa_device_arn = None
        try:
            # Create virtual MFA device
            mfa_device_response = iam_client.create_virtual_mfa_device(VirtualMFADeviceName=mfa_device_name)
            mfa_device_arn = mfa_device_response['VirtualMFADevice']['SerialNumber']

            # Generate QR code (Base32StringSeed)
            qr_code_seed = mfa_device_response['VirtualMFADevice']['Base32StringSeed']

            print(f"Virtual MFA device {mfa_device_name} created with ARN {mfa_device_arn}")
        except Exception as e:
            print(f"Error creating virtual MFA device: {str(e)}")

        # Step 7.2: Activate the MFA device (User must scan QR code and provide codes)
        # You will need to simulate or perform the actual scanning of the QR code to obtain the two codes.
        # For example, use Google Authenticator or AWS MFA to scan the QR code (Base32StringSeed) and provide two subsequent codes.
        # Example input for the two codes:
        mfa_code_1 = input("Enter the first MFA code from your authenticator: ")
        mfa_code_2 = input("Enter the second MFA code from your authenticator: ")

        iam_client.enable_mfa_device(
            UserName=user_name,
            SerialNumber=mfa_device_arn,
            AuthenticationCode1=mfa_code_1,
            AuthenticationCode2=mfa_code_2
        )

        print(f"MFA device enabled for user {user_name} with serial {mfa_device_arn}")

def delete_iam_user(user_name):

    # Step 1: Delete the user's login profile
    try:
        iam_client.delete_login_profile(UserName=user_name)
        print(f"Login profile for {user_name} deleted.")
    except iam_client.exceptions.NoSuchEntityException:
        print(f"No login profile found for {user_name}.")

    # Step 2: Delete the user's access keys
    access_keys = iam_client.list_access_keys(UserName=user_name)
    for key in access_keys['AccessKeyMetadata']:
        iam_client.delete_access_key(UserName=user_name, AccessKeyId=key['AccessKeyId'])
        print(f"Access key {key['AccessKeyId']} deleted.")

    # Step 3: Detach all managed policies from the user
    attached_policies = iam_client.list_attached_user_policies(UserName=user_name)
    for policy in attached_policies['AttachedPolicies']:
        iam_client.detach_user_policy(UserName=user_name, PolicyArn=policy['PolicyArn'])
        print(f"Detached policy {policy['PolicyName']} from {user_name}.")

    # Step 4: Delete all inline policies for the user
    inline_policies = iam_client.list_user_policies(UserName=user_name)
    for policy_name in inline_policies['PolicyNames']:
        iam_client.delete_user_policy(UserName=user_name, PolicyName=policy_name)
        print(f"Deleted inline policy {policy_name} from {user_name}.")

    # Step 5: Remove the user from all groups
    groups = iam_client.list_groups_for_user(UserName=user_name)
    for group in groups['Groups']:
        iam_client.remove_user_from_group(GroupName=group['GroupName'], UserName=user_name)
        print(f"Removed {user_name} from group {group['GroupName']}.")

    # Step 6: Delete MFA devices (if any)
    mfa_devices = iam_client.list_mfa_devices(UserName=user_name)
    for mfa_device in mfa_devices['MFADevices']:
        iam_client.deactivate_mfa_device(UserName=user_name, SerialNumber=mfa_device['SerialNumber'])
        iam_client.delete_virtual_mfa_device(SerialNumber=mfa_device['SerialNumber'])
        print(f"Deleted MFA device {mfa_device['SerialNumber']} for {user_name}.")

    # Step 7: Finally, delete the user
    iam_client.delete_user(UserName=user_name)
    print(f"User {user_name} deleted.")


#=============================================================================
def create_all_iams(lambda_role_name, step_function_role_name):


    CONFIG_PATH = 'service_resources.yml'
    CONFIG = load_from_yaml(CONFIG_PATH)

    lambda_role_name = lambda_role_name
    step_function_role_name = step_function_role_name

    lambda_trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }

    stepfunctions_trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "states.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }

    lambda_role_arn = create_iam_role(lambda_role_name, lambda_trust_policy, "Role for Lambda execution")
    step_function_role_arn = create_iam_role(step_function_role_name, stepfunctions_trust_policy, "Role for Step Functions execution")
    
    time.sleep(5)
    if not lambda_role_arn: print('LAMBDA_ROLE_ARN =================== Empty !!!!!!')
    if not step_function_role_arn: print('STEP_FUNCTION_ROLE_ARN =================== Empty !!!!!!')

    lambda_policy_arn = 'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
    dynamodb_policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
    sns_policy_arn = "arn:aws:iam::aws:policy/AmazonSNSFullAccess"
    sqs_policy_arn = "arn:aws:iam::aws:policy/AmazonSQSFullAccess"
    states_policy_arn = "arn:aws:iam::aws:policy/AWSStepFunctionsFullAccess"


    attach_policy_to_role(lambda_policy_arn, lambda_role_name)
    attach_policy_to_role(dynamodb_policy_arn, lambda_role_name)
    attach_policy_to_role(sns_policy_arn, lambda_role_name)
    attach_policy_to_role(sqs_policy_arn, lambda_role_name)

    CONFIG['iam']['lambda_role_arn'] = lambda_role_arn
    CONFIG['iam']['lambda_role_name'] = lambda_role_name
    CONFIG['iam']['step_function_role_arn'] = step_function_role_arn
    CONFIG['iam']['step_function_role_name'] = step_function_role_name
    
    save_to_yaml(CONFIG_PATH, CONFIG)

def destroy_all_iams():
    delete_iam_role(CONFIG['iam']['lambda_role_name'])
    delete_iam_role(CONFIG['iam']['step_function_role_name'])
    delete_iam_policy(CONFIG['iam']['step_function_invoke_lambda_policy'])
#=============================================================================


if __name__ == '__main__':
    pass
    # create_all_iams()
    # destroy_all_iams()