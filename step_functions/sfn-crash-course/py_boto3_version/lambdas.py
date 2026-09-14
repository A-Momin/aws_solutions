import boto3
import botocore
import os, json, time, copy
from misc import load_from_yaml, save_to_yaml

## ============================================================================

CONFIG_PATH = 'service_resources.yml'
CONFIG = load_from_yaml(CONFIG_PATH)

lambda_client = boto3.client('lambda')

## ============================================================================

# 2. Create Lambda functions
def create_or_update_lambda_function(func_name, handler, role_arn, zip_file):
    try:
        # Check if function already exists
        lambda_client.get_function(FunctionName=func_name)
        # If function exists, update its code
        response = lambda_client.update_function_code(
            FunctionName=func_name,
            ZipFile=open(zip_file, 'rb').read(),
        )

        print(f"Updated Lambda function {func_name}.")
        return response['FunctionArn']
    except lambda_client.exceptions.ResourceNotFoundException:
        # If function does not exist, create it
        response = lambda_client.create_function(
            FunctionName=func_name,
            Runtime='python3.9',
            Role=role_arn,
            Handler=handler,
            Code={'ZipFile': open(zip_file, 'rb').read()},
            Timeout=300,
        )

        print(f"Created Lambda function {func_name}.")
        return response['FunctionArn']
    except Exception as e:
        print(f"Error creating or updating Lambda function {func_name}: {e}")

def delete_lambda_function(function_name):
    """
    Deletes an AWS Lambda function.

    Args:
        function_name (str): The name of the Lambda function to delete.
    """

    try:
        # Delete the Lambda function
        response = lambda_client.delete_function(
            FunctionName=function_name
        )
        print(f"Deleted Lambda function: {function_name}")
    except botocore.exceptions.ClientError as error:
        print(f"Error deleting Lambda function {function_name}: {error}")

def wait_for_lambda_function_creation(func_name):
    while True:
        try:
            response = lambda_client.get_function(FunctionName=func_name)
            if response['Configuration']['State'] == 'Active':
                print(f"Lambda function {func_name} is active.")
                break
            else:
                print(f"Waiting for Lambda function {func_name} to become active...")
        except lambda_client.exceptions.ResourceNotFoundException:
            print(f"Lambda function {func_name} not found yet. Waiting...")
        time.sleep(5)

def create_all_lambdas():
    # Replace with the actual path to your Lambda deployment packages
    lambda_functions = {
        'checkInventory': 'handlers.check_inventory',
        'calculateTotal': 'handlers.calculate_total',
        'redeemPoints': 'handlers.redeem_points',
        'billCustomer': 'handlers.bill_customer',
        'restoreRedeemPoints': 'handlers.restore_redeem_points',
        'restoreQuantity': 'handlers.restore_quantity',
        'sqsWorker': 'handlers.sqs_worker'
    }

    lambda_arns = {}
    lambda_role_arn = CONFIG['iam']['lambda_role_arn']

    for func, handler in lambda_functions.items():
        lambda_arns[func] = create_or_update_lambda_function(func, handler, lambda_role_arn, 'handlers.zip')
        # wait_for_lambda_function_creation(func)
        if not lambda_arns[func]: print(f"LAMBDA_ARN for {func}=================== Empty !!!!!!")
        CONFIG['lambda_functions'][func] = lambda_arns[func]


    print(f"Module: {__name__}\n")
    print(f"CONFIG: \n{CONFIG}\n")
    save_to_yaml(CONFIG_PATH, CONFIG)


def destroy_all_lambdas():
    lambda_functions = CONFIG['lambda_functions']
    for func in lambda_functions:
        delete_lambda_function(func)


if __name__ == '__main__':
    create_all_lambdas()
    # destroy_all_lambdas()