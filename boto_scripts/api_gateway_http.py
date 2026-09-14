import boto3
from botocore.exceptions import ClientError
import json, os
from misc import load_from_yaml, save_to_yaml
# =============================================================================
INPUTS_PATH = 'inputs.yml'
INPUTS = load_from_yaml(INPUTS_PATH)
account_id = os.environ['AWS_ACCOUNT_ID_ROOT']
region = os.environ['AWS_DEFAULT_REGION']
# =============================================================================

# Initialize Boto3 clients for Lambda and IAM
lambda_client = boto3.client('lambda')
iam_client = boto3.client('iam')

# Initialize Boto3 clients for API Gateway and Lambda
apigateway_client = boto3.client('apigatewayv2')


def create_http_api(api_name, description=None, protocol_type='HTTP', route_selection_expression=None, tags=None, cors_configuration=None):
    """
    Creates an AWS API Gateway HTTP API.

    Parameters:
    api_name (str): The name of the API.
    description (str): The description of the API (optional).
    protocol_type (str): The protocol type (default is 'HTTP').
    route_selection_expression (str): The route selection expression for the API (optional).
    tags (dict): The tags to apply to the API (optional).
    cors_configuration (dict): The CORS configuration for the API (optional).

    Returns:
    dict: Response from the create_api call.
    """

    # Build the request parameters
    params = {
        'Name': api_name,
        'ProtocolType': protocol_type
    }

    if description: params['Description'] = description
    if route_selection_expression: params['RouteSelectionExpression'] = route_selection_expression
    if tags: params['Tags'] = tags
    if cors_configuration: params['CorsConfiguration'] = cors_configuration

    try:
        response = apigateway_client.create_api(**params)
        print(f"API with ID {response['ApiId']} created successfully.")
        return response
    except Exception as e:
        print(f"An error occurred: {e}")

def create_http_api_with_lambda_integration(api_name, lambda_arn, region_name=region):
    # Create the HTTP API
    api_response = apigateway_client.create_api(
        Name=api_name,
        ProtocolType='HTTP',
        CorsConfiguration={
            'AllowOrigins': ['*'],
            'AllowMethods': ['GET', 'POST', 'OPTIONS'],
            'AllowHeaders': ['Content-Type', 'X-Amz-Date', 'Authorization', 'X-Api-Key', 'X-Amz-Security-Token'],
        }
    )
    api_id = api_response['ApiId']
    print(f"Created API with ID: {api_id}")

    # Create integration
    integration_response = apigateway_client.create_integration(
        ApiId=api_id,
        IntegrationType='AWS_PROXY',
        IntegrationUri=f'arn:aws:apigateway:{region_name}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations',
        IntegrationMethod='POST',
        PayloadFormatVersion='2.0'
    )
    integration_id = integration_response['IntegrationId']
    print(f"Created integration with ID: {integration_id}")

    # Create routes
    get_route_response = apigateway_client.create_route(
        ApiId=api_id,
        RouteKey='GET /getPerson',
        Target=f'integrations/{integration_id}'
    )
    print(f"Created GET /getPerson route")

    post_route_response = apigateway_client.create_route(
        ApiId=api_id,
        RouteKey='POST /createPerson',
        Target=f'integrations/{integration_id}'
    )
    print(f"Created POST /createPerson route")

    # Create a stage and deploy the API
    stage_name = 'dev'
    stage_response = apigateway_client.create_stage(
        ApiId=api_id,
        StageName=stage_name,
        AutoDeploy=False
    )
    print(f"Created stage: {stage_name}")
    
    deployment_response = apigateway_client.create_deployment(
        ApiId=api_id,
        StageName=stage_name
    )
    print(f"Deployed API to stage: {stage_name}")

    return api_response

def delete_http_api(api_id):
    """
    Deletes an AWS API Gateway HTTP API.

    Parameters:
    api_id (str): The ID of the API to be deleted.

    Returns:
    dict: Response from the delete_api call.
    """

    try:
        response = apigateway_client.delete_api(ApiId=api_id)

        print(f"API with ID {api_id} deleted successfully.")
        return response
    except apigateway_client.exceptions.NotFoundException:
        print(f"API with ID {api_id} not found.")
    except apigateway_client.exceptions.BadRequestException as e:
        print(f"Bad request: {e}")
    except apigateway_client.exceptions.TooManyRequestsException as e:
        print(f"Too many requests: {e}")
    except apigateway_client.exceptions.UnauthorizedException as e:
        print(f"Unauthorized: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def add_invoke_permissions_to_lambda_for_all_routes(lambda_function_name, api_id, stage_name):
    """
    Adds permission to an AWS Lambda function to be invoked by all routes of an API Gateway HTTP API.

    :param lambda_function_name: The name of the Lambda function.
    :param api_id: The ID of the API Gateway HTTP API.
    :param stage_name: The name of the deployment stage.
    """
    # Initialize the Lambda and API Gateway clients
    lambda_client = boto3.client('lambda')
    apigateway_client = boto3.client('apigatewayv2')

    # Retrieve all routes for the specified API Gateway HTTP API
    try:
        routes_response = apigateway_client.get_routes(ApiId=api_id)
        routes = routes_response['Items']
    except boto3.exceptions.Boto3Error as e:
        print(f"An error occurred while retrieving routes: {e}")
        return None

    # Loop through each route and add permission to the Lambda function
    for route in routes:
        route_key = route['RouteKey']
        source_arn = f"arn:aws:execute-api:{boto3.Session().region_name}:{boto3.client('sts').get_caller_identity()['Account']}:{api_id}/{stage_name}/{route_key}"

        try:
            response = lambda_client.add_permission(
                FunctionName=lambda_function_name,
                StatementId=f"{lambda_function_name}-invoke-permission-{route_key.replace(' ', '').replace('/', '')}",
                Action="lambda:InvokeFunction",
                Principal="apigateway.amazonaws.com",
                SourceArn=source_arn
            )
            print(f"Added invoke permission to Lambda function '{lambda_function_name}' for route '{route_key}'")
        except boto3.exceptions.Boto3Error as e:
            print(f"An error occurred while adding permission for route '{route_key}': {e}")


def create_all():

    # Create IAM role for Lambda function
    role_name = 'persons_hhtpapi_role'
    function_name = "persons_hhtpapi_lambda"
    zip_file_path = "lambdahandler.zip"


    role_arn = create_lambda_role(role_name)
    INPUTS["role_name"] = role_name
    INPUTS["role_arn"] = role_arn


    lambda_arn = create_lambda_function(function_name, role_arn, zip_file_path)['FunctionArn']
    INPUTS["function_name"] = function_name
    INPUTS["lambda_arn"] = lambda_arn


    api_name='persons_api'
    response = create_http_api_with_lambda_integration(api_name, lambda_arn)

    api_id = response["ApiId"]

    INPUTS["api_id"] = response["ApiId"]

    stage = 'dev'
    add_invoke_permissions_to_lambda_for_all_routes(function_name, api_id, stage)
    
    INPUTS["stage"] = stage


    save_to_yaml(INPUTS_PATH, INPUTS)


def delete_all():

    api_id = INPUTS["api_id"]
    role_name = INPUTS["role_name"]
    function_name = INPUTS["function_name"]
    delete_iam_role(role_name)
    delete_lambda_function(function_name)
    delete_http_api(api_id)


# create_all()
# delete_all()