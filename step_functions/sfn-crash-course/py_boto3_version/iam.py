import boto3
import botocore
from botocore.exceptions import ClientError
import os, time, json
from misc import load_from_yaml, save_to_yaml

## ============================================================================

CONFIG_PATH = 'service_resources.yml'
CONFIG = load_from_yaml(CONFIG_PATH)

# Initialize boto3 clients
iam_client = boto3.client('iam')
lambda_client = boto3.client('lambda')

account_id = os.environ['AWS_ACCOUNT_ID_ROOT']
region = os.environ['AWS_DEFAULT_REGION']

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


def attach_role_policy(role_name, policy_arn):
    iam_client.attach_role_policy(
        RoleName=role_name,
        PolicyArn=policy_arn
    )

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
    # Initialize the IAM client
    iam_client = boto3.client('iam')

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

def create_all_iams(lambda_role_name, step_function_role_name):

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


    attach_role_policy(lambda_role_name, lambda_policy_arn)
    attach_role_policy(lambda_role_name, dynamodb_policy_arn)
    attach_role_policy(lambda_role_name, sns_policy_arn)
    attach_role_policy(lambda_role_name, sqs_policy_arn)

    CONFIG['iam']['lambda_role_arn'] = lambda_role_arn
    CONFIG['iam']['lambda_role_name'] = lambda_role_name
    CONFIG['iam']['step_function_role_arn'] = step_function_role_arn
    CONFIG['iam']['step_function_role_name'] = step_function_role_name
    
    save_to_yaml(CONFIG_PATH, CONFIG)


def destroy_all_iams():
    delete_iam_role(CONFIG['iam']['lambda_role_name'])
    delete_iam_role(CONFIG['iam']['step_function_role_name'])
    delete_iam_policy(CONFIG['iam']['step_function_invoke_lambda_policy'])


if __name__ == '__main__':
    pass
    # create_all_iams()
    # destroy_all_iams()