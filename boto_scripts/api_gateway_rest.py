import boto3
import json, os
from misc import load_from_yaml, save_to_yaml
# =============================================================================
INPUTS_PATH = 'inputs.yml'
INPUTS = load_from_yaml(INPUTS_PATH)
INPUTS = {} if not INPUTS else INPUTS
account_id = os.environ['AWS_ACCOUNT_ID_ROOT']
region = os.environ['AWS_DEFAULT_REGION']
# =============================================================================

# Initialize Boto3 clients for API Gateway and Lambda
apigateway_client = boto3.client('apigateway')
lambda_client = boto3.client('lambda')


def create_rest_api(api_name, description=None, version=None, api_key_source=None, endpoint_configuration=None, tags=None, binary_media_types=None):
    params = {'name': api_name}
    if description: params['description'] = description
    if version: params['version'] = version
    if api_key_source: params['apiKeySource'] = api_key_source
    if endpoint_configuration: params['endpointConfiguration'] = endpoint_configuration
    if tags: params['tags'] = tags
    if binary_media_types: params['binaryMediaTypes'] = binary_media_types

    response = apigateway_client.create_rest_api(**params)
    return response

def delete_rest_api(api_id):
    """
    Deletes an API Gateway REST API.

    :param api_id: The ID of the REST API to delete.
    :return: Response from the delete_rest_api call.
    """
    try:
        response = apigateway_client.delete_rest_api(
            restApiId=api_id
        )
        print(f"Deleted REST API with ID: {api_id}")
        return response
    except Exception as e:
        print(f"Error deleting REST API: {e}")

def create_resource(api_id, parent_id, path_part):
    response = apigateway_client.create_resource(
        restApiId=api_id,
        parentId=parent_id,
        pathPart=path_part
    )
    return response

def create_method(api_id, resource_id, http_method, authorization_type='NONE', api_key_required=False, request_parameters=None):
    response = apigateway_client.put_method(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod=http_method,
        authorizationType=authorization_type,
        apiKeyRequired=api_key_required,
        requestParameters=request_parameters or {}
    )
    return response

def create_integration(api_id, resource_id, http_method, lambda_arn):
    region = boto3.Session().region_name
    uri = f'arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations'
    
    response = apigateway_client.put_integration(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod=http_method,
        type='AWS_PROXY',
        uri=uri,
        integrationHttpMethod='POST'
    )
    
    return response

def create_deployment(api_id, stage_name):
    response = apigateway_client.create_deployment(
        restApiId=api_id,
        stageName=stage_name
    )
    return response

def add_invoke_permission_to_lambda(function_name, api_gateway_arn):
    response = lambda_client.add_permission(
        FunctionName=function_name,
        StatementId='APIGatewayInvokePermission',
        Action='lambda:InvokeFunction',
        Principal='apigateway.amazonaws.com',
        SourceArn=api_gateway_arn
    )
    return response

def create_all_rest_api():

    # Example usage
    api_name = 'transaction_rest_api'
    description = 'My REST API Description'
    version = '1.0'
    endpoint_configuration = {'types': ['REGIONAL']}
    stage_name = 'dev'
    INPUTS['api_stage'] = stage_name
    INPUTS['api_protocol'] = 'REST'
    INPUTS['api_resource'] = 'transactions'

    # Create the REST API
    api_response = create_rest_api(api_name, description, version, endpoint_configuration=endpoint_configuration)
    api_id = api_response['id']
    INPUTS['api_id'] = api_id
    api_gateway_arn = f"arn:aws:execute-api:us-east-1:381492255899:{api_id}"
    print("api_gateway_arn: ", api_gateway_arn)
    INPUTS['api_gateway_arn'] = api_gateway_arn


    # Get the root resource ID
    resources = apigateway_client.get_resources(restApiId=api_id)
    root_id = next(item['id'] for item in resources['items'] if item['path'] == '/')

    # Create a resource
    resource_name = "transactions"
    resource_response = create_resource(api_id, root_id, resource_name)
    print('API Resource Response: ', resource_response)
    resource_id = resource_response['id']
    INPUTS['api_resource'] = resource_name

    # Create a method for the resource
    http_method = 'GET'
    INPUTS['api_method'] = http_method

    method_response = create_method(api_id, resource_id, http_method)

    # Create a Lambda integration for the method
    lambda_arn = INPUTS["lambda_arn"]
    integration_response = create_integration(api_id, resource_id, http_method, lambda_arn)


    # Create a stage and deploy the API
    deployment_response = create_deployment(api_id, stage_name)

    # Example usage
    function_name = INPUTS['function_name']
    api_gateway_arn = f"arn:aws:execute-api:us-east-1:{account_id}:{api_id}/*/{http_method}/{resource_name}"
    # print(api_gateway_arn)
    # api_gateway_arn = f"arn:aws:execute-api:us-east-1:381492255899:{api_id}/*/GET/transactions"

    response = add_invoke_permission_to_lambda(function_name, api_gateway_arn)

    save_to_yaml(INPUTS_PATH, INPUTS)

def create_api_gateway_model(api_id, model_name, description, content_type, schema):
    """
    Creates a Model for a REST API in AWS API Gateway.

    Args:
        api_id (str): The ID of the API in which the model will be created.
        model_name (str): The name of the model.
        description (str): A description for the model.
        content_type (str): The content type of the model (e.g., 'application/json').
        schema (dict): The schema definition for the model in JSON schema format.

    Returns:
        dict: The response from the `create_model` API call.
    """
    
    # Initialize the boto3 client for API Gateway
    api_client = boto3.client('apigateway')

    # Create the model
    response = api_client.create_model(
        restApiId=api_id,
        name=model_name,
        description=description,
        contentType=content_type,
        schema=json.dumps(schema)  # Convert schema dictionary to JSON string
    )

    return response

def create_request_validator(api_id, validator_name, validate_request_body=True, validate_request_parameters=True):
    """
    Creates a request validator in API Gateway.

    Args:
        api_id (str): The ID of the API where the validator will be created.
        validator_name (str): The name for the request validator.
        validate_request_body (bool): Whether to validate the request body.
        validate_request_parameters (bool): Whether to validate the request parameters.

    Returns:
        str: The ID of the created request validator.
    """
    
    # Initialize the boto3 client for API Gateway
    api_client = boto3.client('apigateway')

    # Create a request validator
    response = api_client.create_request_validator(
        restApiId=api_id,
        name=validator_name,
        validateRequestBody=validate_request_body,
        validateRequestParameters=validate_request_parameters
    )

    # Return the ID of the created validator
    return response['id']

def attach_request_validator_to_method(api_id, resource_id, http_method, request_validator_id):
    """
    Attaches a request validator to an existing method in API Gateway.

    Args:
        api_id (str): The ID of the API containing the method.
        resource_id (str): The resource ID for the method's resource.
        http_method (str): The HTTP method (GET, POST, etc.) for which to apply the validator.
        request_validator_id (str): The ID of the request validator to apply.

    Returns:
        dict: The response from the `update_method` API call.
    """
    
    # Initialize the boto3 client for API Gateway
    api_client = boto3.client('apigateway')

    # Update the method to include the request validator
    response = api_client.update_method(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod=http_method,
        patchOperations=[
            {
                'op': 'replace',
                'path': '/requestValidatorId',
                'value': request_validator_id
            }
        ]
    )

    return response



# print(f"API ID: {api_id}")
# print(f"Resource ID: {resource_id}")
# print(f"Deployment ID: {deployment_response['id']}")

# create_all_rest_api()
# delete_rest_api(INPUTS['api_id'])
