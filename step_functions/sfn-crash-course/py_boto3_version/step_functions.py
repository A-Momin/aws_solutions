#==============================================================================
import botocore
from botocore.exceptions import ClientError
import boto3
import json
import os
from misc import load_from_yaml, save_to_yaml

## ============================================================================

CONFIG_PATH = 'service_resources.yml'
CONFIG = load_from_yaml(CONFIG_PATH)
account_id = os.environ['AWS_ACCOUNT_ID_ROOT']
region = os.environ['AWS_DEFAULT_REGION']
    

# Initialize boto3 clients
stepfunctions_client = boto3.client('stepfunctions')

def delete_step_function(state_machine_arn):
    """
    Deletes an AWS Step Function (state machine).

    Args:
        state_machine_arn (str): The ARN of the state machine to delete.
    """

    try:
        # Delete the state machine
        response = stepfunctions_client.delete_state_machine(
            stateMachineArn=state_machine_arn
        )
        print(f"Deleted state machine: {state_machine_arn}")
    except botocore.exceptions.ClientError as error:
        print(f"Error deleting state machine {state_machine_arn}: {error}")


def grant_stepfunction_invoke_lambda_permissions(state_machine_arn, role_name, lambda_function_arns):
    # Initialize the IAM and Step Functions clients
    iam_client = boto3.client('iam')
    sf_client = boto3.client('stepfunctions')

    # Construct the policy document for Step Functions
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "states:StartExecution",
                "Resource": state_machine_arn
            }
        ]
    }

    # Add Lambda permissions to the policy document
    for lambda_arn in lambda_function_arns:
        policy_statement = {
            "Effect": "Allow",
            "Action": "lambda:InvokeFunction",
            "Resource": lambda_arn
        }
        policy_document['Statement'].append(policy_statement)

    # Convert policy document to JSON string
    policy_json = json.dumps(policy_document)

    # Create a policy
    try:
        policy_response = iam_client.create_policy(
            PolicyName='StepFunctionInvokeLambdaPolicy',
            PolicyDocument=policy_json,
            Description='Allows Step Functions to invoke Lambda functions'
        )
        policy_arn = policy_response['Policy']['Arn']
        CONFIG['iam']['step_function_invoke_lambda_policy'] = policy_arn
        save_to_yaml(CONFIG_PATH, CONFIG)

        # Attach the policy to the Step Functions role
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_arn
        )

        print(f"Successfully granted permissions to {role_name} role for Step Functions and Lambda functions.")
    
    except ClientError as e:
        print(f"ClientError: {e}")
    except Exception as e:
        print(f"Error: {e}")


def create_all_states():
    lambda_arns = CONFIG['lambda_functions']
    step_function_role_arn = CONFIG['iam']['step_function_role_arn']


    # 3. Create Step Functions state machine
    state_machine_definition = {
        "Comment": "Store Checkout Flow",
        "StartAt": "checkInventory",
        "States": {
            "checkInventory": {
                "Type": "Task",
                "Resource": lambda_arns['checkInventory'],
                "Catch": [
                    {
                        "ErrorEquals": ["BookNotFound"],
                        "Next": "BookNotFoundError"
                    },
                    {
                        "ErrorEquals": ["BookOutOfStock"],
                        "Next": "BookOutOfStockError"
                    }
                ],
                "ResultPath": "$.book",
                "Next": "calculateTotal"
            },
            "calculateTotal": {
                "Type": "Task",
                "Resource": lambda_arns['calculateTotal'],
                "ResultPath": "$.total",
                "Next": "isRedeemNeeded"
            },
            "isRedeemNeeded": {
                "Type": "Choice",
                "Choices": [
                    {
                        "Variable": "$.redeem",
                        "BooleanEquals": True,
                        "Next": "RedeemPoints"
                    }
                ],
                "Default": "BillCustomer"
            },
            "RedeemPoints": {
                "Type": "Task",
                "Resource": lambda_arns['redeemPoints'],
                "ResultPath": "$.total",
                "Catch": [
                    {
                        "ErrorEquals": ["States.ALL"],
                        "Next": "RedeemPointsError"
                    }
                ],
                "Next": "BillCustomer"
            },
            "BillCustomer": {
                "Type": "Task",
                "Resource": lambda_arns['billCustomer'],
                "ResultPath": "$.billingStatus",
                "Retry": [
                    {
                        "ErrorEquals": ["States.ALL"],
                        "MaxAttempts": 0
                    }
                ],
                "Catch": [
                    {
                        "ErrorEquals": ["States.ALL"],
                        "ResultPath": "$.customerBilling",
                        "Next": "BillingError"
                    }
                ],
                "Next": "PrepareOrder"
            },
            "PrepareOrder": {
                "Type": "Task",
                "Resource": "arn:aws:states:::sqs:sendMessage.waitForTaskToken",
                "Parameters": {
                    "QueueUrl": f"https://sqs.{region}.amazonaws.com/{account_id}/OrdersQueue",
                    "MessageBody": {
                        "Input.$": "$",
                        "Token.$": "$$.Task.Token"
                    }
                },
                "ResultPath": "$.courierStatus",
                "Catch": [
                    {
                        "ErrorEquals": ["NoCourierAvailable"],
                        "ResultPath": "$.courierError",
                        "Next": "RefundCustomer"
                    }
                ],
                "Next": "DispatchOrder"
            },
            "DispatchOrder": {
                "Type": "Task",
                "Resource": "arn:aws:states:::sns:publish",
                "Parameters": {
                    "TopicArn": f"arn:aws:sns:{region}:{account_id}:NotifyCourier",
                    "Message.$": "$"
                },
                "Next": "Dispatched"
            },
            "Dispatched": {
                "Type": "Pass",
                "Result": "Your order will be dispatched in 24 hours",
                "End": True
            },
            "RestoreRedeemPoints": {
                "Type": "Task",
                "Resource": lambda_arns['restoreRedeemPoints'],
                "End": True
            },
            "RestoreQuantity": {
                "Type": "Task",
                "Resource": lambda_arns['restoreQuantity'],
                "ResultPath": "$.quantityRestoreStatus",
                "Next": "RestoreRedeemPoints"
            },
            "RefundCustomer": {
                "Type": "Pass",
                "Result": "Customer is refunded",
                "ResultPath": "$.refundStatus",
                "Next": "RestoreQuantity"
            },
            "BookNotFoundError": {
                "Type": "Pass",
                "Result": "No such book available",
                "End": True
            },
            "BookOutOfStockError": {
                "Type": "Pass",
                "Result": "Sorry, the book is out of stock",
                "End": True
            },
            "RedeemPointsError": {
                "Type": "Pass",
                "Result": "Error in redeeming points",
                "End": True
            },
            "BillingError": {
                "Type": "Pass",
                "Result": "Billing error",
                "ResultPath": "$.billingStatus",
                "Next": "RestoreRedeemPoints"
            }
        }
    }

    state_machine_arn = stepfunctions_client.create_state_machine(
        name="storeCheckoutFlow",
        definition=json.dumps(state_machine_definition),
        roleArn=step_function_role_arn
    )['stateMachineArn']


    step_function_role_name = CONFIG['iam']['step_function_role_name']
    grant_stepfunction_invoke_lambda_permissions(state_machine_arn, step_function_role_name, lambda_arns.values())

    CONFIG['step_function']['state_machine_arn'] = state_machine_arn
    save_to_yaml(CONFIG_PATH, CONFIG)

if __name__ == '__main__':
    create_all_states()
    # destroy_all_states()
    # Example usage
    # state_machine_arn = CONFIG['step_function']['state_machine_arn']
    # delete_step_function(state_machine_arn)
