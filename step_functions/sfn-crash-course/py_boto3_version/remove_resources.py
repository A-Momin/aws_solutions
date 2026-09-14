import boto3
import os

from dynamodb import delete_dynamodb_table
from sqs import delete_message_from_sqs_queue, delete_sqs_queue
from sns import delete_sns_topic
## ============================================================================

# Initialize boto3 clients
iam_client = boto3.client('iam')
lambda_client = boto3.client('lambda')
stepfunctions_client = boto3.client('stepfunctions')

# AWS account and region information
account_id = os.environ['AWS_ACCOUNT_ID_ROOT']
region = os.environ['AWS_DEFAULT_REGION']

# List of Lambda functions to delete
lambda_functions = [
    'checkInventory',
    'calculateTotal',
    'redeemPoints',
    'billCustomer',
    'restoreRedeemPoints',
    'restoreQuantity',
    'sqsWorker'
]

# Role names to delete
iam_roles = [
    'LambdaExecutionRole',
    'StepFunctionsExecutionRole'
]

# Step Functions state machine name
state_machine_name = 'storeCheckoutFlow'

# Detach policies from IAM role
def detach_role_policy(role_name, policy_arn):
    try:
        iam_client.detach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
        print(f"Detached policy {policy_arn} from role {role_name}.")
    except iam_client.exceptions.NoSuchEntityException:
        print(f"Policy {policy_arn} not found on role {role_name}.")
    except Exception as e:
        print(f"Error detaching policy {policy_arn} from role {role_name}: {e}")

# Delete IAM role
def delete_iam_role(role_name):
    try:
        response = iam_client.delete_role(RoleName=role_name)
        print(f"Deleted IAM role {role_name}.")
    except iam_client.exceptions.NoSuchEntityException:
        print(f"IAM role {role_name} does not exist.")
    except Exception as e:
        print(f"Error deleting IAM role {role_name}: {e}")

# Delete Lambda function
def delete_lambda_function(function_name):
    try:
        response = lambda_client.delete_function(FunctionName=function_name)
        print(f"Deleted Lambda function {function_name}.")
    except lambda_client.exceptions.ResourceNotFoundException:
        print(f"Lambda function {function_name} does not exist.")
    except Exception as e:
        print(f"Error deleting Lambda function {function_name}: {e}")

# Delete Step Functions state machine
def delete_state_machine(state_machine_name):
    try:
        # Get the ARN of the state machine
        response = stepfunctions_client.list_state_machines()
        for sm in response['stateMachines']:
            if sm['name'] == state_machine_name:
                state_machine_arn = sm['stateMachineArn']
                stepfunctions_client.delete_state_machine(stateMachineArn=state_machine_arn)
                print(f"Deleted Step Functions state machine {state_machine_name}.")
                return
        print(f"State machine {state_machine_name} not found.")
    except Exception as e:
        print(f"Error deleting state machine {state_machine_name}: {e}")

# Main logic
def main():
    # Detach policies from IAM roles
    policies_to_detach = [
        'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
        'arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess',
        'arn:aws:iam::aws:policy/AmazonSNSFullAccess',
        'arn:aws:iam::aws:policy/AmazonSQSFullAccess',
        'arn:aws:iam::aws:policy/AWSStepFunctionsFullAccess'
    ]

    for role in iam_roles:
        for policy in policies_to_detach:
            detach_role_policy(role, policy)

    # Delete Lambda functions
    for func in lambda_functions:
        delete_lambda_function(func)

    # Delete Step Functions state machine
    delete_state_machine(state_machine_name)

    # Delete IAM roles
    for role in iam_roles:
        delete_iam_role(role)
    
    # Delete Dynamodb
    user_table_name = 'userTable'
    book_table_name = 'bookTable'
    delete_dynamodb_table(user_table_name)
    delete_dynamodb_table(book_table_name)

    # # Clean up by deleting the SNS topic
    topic_arn = f"arn:aws:sns:{region}:{account_id}:NotifyCourier"
    delete_sns_topic(topic_arn)

    # # Clean up by deleting the SQS queue
    queue_url = f"https://sqs.{region}.amazonaws.com/{account_id}/OrdersQueue"
    delete_sqs_queue(queue_url)

if __name__ == "__main__":
    main()
