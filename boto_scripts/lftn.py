import os
import boto3
import botocore
from botocore.exceptions import ClientError

# =============================================================================
ACCOUNT_ID = os.environ["AWS_ACCOUNT_ID_ROOT"]
REGION = os.environ["AWS_DEFAULT_REGION"]
VPC_ID = os.environ["AWS_DEFAULT_VPC"]
SECURITY_GROUP_ID = os.environ["AWS_DEFAULT_SG_ID"]
SUBNET_IDS = SUBNET_IDS = os.environ["AWS_DEFAULT_SUBNET_IDS"].split(":")
SUBNET_ID = SUBNET_IDS[0]

glue_client = boto3.client("glue")
lakeformation_client = boto3.client("lakeformation")
sts_client = boto3.client("sts")
# =============================================================================

LFTN_ADMIN_ARN = f"arn:aws:iam::{ACCOUNT_ID}:user/AMominNJ"  # or role ARN

def add_lakeformation_admin(admin_arn):
    try:
        lakeformation_client.put_data_lake_settings(
            DataLakeSettings={
                "DataLakeAdmins": [{"DataLakePrincipalIdentifier": admin_arn}]
            }
        )
        print("✅ Successfully added as Lake Formation admin.")
    except Exception as e:
        print("❌ Failed to add admin:", str(e))

# add_lakeformation_admin(LFTN_ADMIN_ARN)


def create_glue_database(database_name, catalog_id=None, description=None, location_uri=None, parameters=None, use_only_iam_access_control=False):
    """
    Create a database in AWS Glue.

    :param catalog_id: The ID of the Data Catalog in which to create the database.
    :param database_name: The name of the database.
    :param description: (Optional) A description of the database.
    :param location_uri: (Optional) The location of the database.
    :param parameters: (Optional) A dictionary of key-value pairs that define parameters and properties of the database.
    :param use_only_iam_access_control: (Optional) Whether to use only IAM access control for new tables in this database.
    :return: Response from the AWS Glue create_database call.
    """

    # Create the database input dictionary
    database_input = {'Name': database_name}

    if description: database_input['Description'] = description

    if location_uri: database_input['LocationUri'] = location_uri

    if parameters: database_input['Parameters'] = parameters

    # Call the create_database function
    response = glue_client.create_database(
        CatalogId=catalog_id,
        DatabaseInput=database_input
    )

    # Set the UseOnlyIamAccessControl property using Lake Formation API
    if use_only_iam_access_control:
        lakeformation_client.update_database(
            CatalogId=catalog_id,
            Name=database_name,
            DatabaseInput={
                'Name': database_name,
                'UseOnlyIamAccessControl': use_only_iam_access_control
            }
        )

    return response

# register the Amazon S3 bucket as your data lake storage
def register_s3_path_as_data_lake_location(s3_path, iam_role='AWSServiceRoleForLakeFormationDataAccess'):
    """
    Register an S3 path as the storage location for your data lake with AWS Lake Formation.

    :param s3_path: The S3 URI of the path (e.g., s3://example-bucket/path/).
    :param iam_role: The IAM role to use for access (default is 'AWSServiceRoleForLakeFormationDataAccess').
    :return: None
    """

    # Convert the S3 path to the bucket ARN
    bucket_name = s3_path.split("//")[1].split("/")[0]
    s3_bucket_arn = f'arn:aws:s3:::{bucket_name}'

    # Get the account ID of the IAM role
    account_id = sts_client.get_caller_identity().get('Account')

    # Construct the ARN for the IAM role
    role_arn = f'arn:aws:iam::{account_id}:role/{iam_role}'

    try:
        response = lakeformation_client.register_resource(
            ResourceArn=s3_bucket_arn,
            UseServiceLinkedRole=True,  # Set to False to use the provided IAM role instead of the service-linked role
            RoleArn=role_arn,
            HybridAccessEnabled=True
        )
        print(f"Location registered successfully: {response}")
    except ClientError as e:
        print(f"Error registering location: {e}")

def grant_permissions(role_user_group_arn, resources, permissions=['ALL'], grantable_permissions=['ALL']):
    """
    Grant database permissions to a role in AWS Lake Formation.

    :param database_name: The name of the database to which permissions are granted.
    :param role_arn: The ARN of the IAM role to which permissions are granted.
    :param permissions: List of permissions to grant (e.g., ['ALL', 'SELECT', 'DESCRIBE']).
    :return: None
    """

    try:
        response = lakeformation_client.grant_permissions(
            CatalogId=None,
            Principal={
                'DataLakePrincipalIdentifier': role_user_group_arn
            },
            Resource=resources,
            Permissions=permissions,
            PermissionsWithGrantOption=grantable_permissions
        )

        print(f"Permissions granted successfully: {response}")
    except ClientError as e:
        print(f"Error granting permissions: {e}")

def grant_database_level_permissions(database_name, role_user_group_arn, permissions):
    """
    Grant database permissions to a role in AWS Lake Formation.

    :param database_name: The name of the database to which permissions are granted.
    :param role_user_group_arn: The ARN of the IAM role to which permissions are granted.
    :param permissions: List of permissions to grant (e.g., ['ALL', 'SELECT', 'DESCRIBE']).
    :return: None
    """

    try:
        response = lakeformation_client.grant_permissions(
            Principal={
                'DataLakePrincipalIdentifier': role_user_group_arn
            },
            Resource={
                'Database': {
                    'Name': database_name
                }
            },
            Permissions=permissions,
            PermissionsWithGrantOption=permissions  # If you want to allow the role to grant these permissions to others
        )
        print(f"Permissions granted successfully: {response}")
    except ClientError as e:
        print(f"Error granting permissions: {e}")

def grant_table_level_permissions(principal, database_name, table_name, permissions=['ALL'], grant_option=False):
    """
    Grant table permissions to an IAM role in AWS Lake Formation.
    
    :param principal: The ARN of the IAM role or user.
    :param database_name: The name of the database in Lake Formation.
    :param table_name: The name of the table in the database.
    :param permissions: A list of permissions to grant (e.g., ['SELECT', 'ALTER']).
    :param grant_option: Boolean to grant permissions with grant option (default is False).
    """

    try:
        # Define the permissions with or without grant option
        permissions_with_grant_option = permissions if grant_option else []
        
        # Grant permissions on the table
        response = lakeformation_client.grant_permissions(
            Principal={
                'DataLakePrincipalIdentifier': principal
            },
            Resource={
                'Table': {
                    'DatabaseName': database_name,
                    'Name': table_name
                }
            },
            Permissions=permissions,
            PermissionsWithGrantOption=permissions_with_grant_option
        )
        
        print(f"Permissions granted successfully to {principal} for table {table_name} in database {database_name}")
        return response

    except Exception as e:
        print(f"Error granting permissions: {e}")


# response = glue_client.delete_table(
#             DatabaseName=database_name,
#             Name=table_name
#         )

# ==============================================================================

# def create_data_cells_filter(
#     catalog_id: str,
#     database_name: str,
#     table_name: str,
#     filter_name: str,
#     column_name: str,
#     allowed_values: list,
#     principal_arn: str,
# ):
#     try:
#         lakeformation_client.create_data_cells_filter(
#             TableData={
#                 "TableCatalogId": catalog_id,
#                 "DatabaseName": database_name,
#                 "TableName": table_name,
#                 "Name": filter_name,
#                 "RowFilter": {
#                     "FilterExpression": f"{column_name} in ({', '.join([repr(v) for v in allowed_values])})"
#                 },
#                 "ColumnNames": [],  # Leave empty to allow all columns (unless you're doing column filtering too)
#                 "ColumnWildcard": {},  # Or use {"ExcludedColumnNames": ["col1", "col2"]}
#             }
#         )
#         print(f"✅ Created Lake Formation Data Cells Filter: {filter_name}")
#     except Exception as e:
#         print(f"❌ Failed to create data filter: {str(e)}")

# lakeformation_client.grant_permissions(
#     Principal={
#         "DataLakePrincipalIdentifier": "arn:aws:iam::123456789012:role/DataAnalystRole"
#     },
#     Resource={
#         "DataCellsFilter": {
#             "TableCatalogId": "123456789012",
#             "DatabaseName": "finance_db",
#             "TableName": "transactions",
#             "Name": "USRegionFilter",
#         }
#     },
#     Permissions=["SELECT"],
# )

# # Example usage
# create_data_cells_filter(
#     catalog_id="123456789012",
#     database_name="finance_db",
#     table_name="transactions",
#     filter_name="USRegionFilter",
#     column_name="region",
#     allowed_values=["US"],  # Only rows where region = 'US' will be visible
#     principal_arn="arn:aws:iam::123456789012:role/DataAnalystRole",
# )

#==============================================================================

# principal_arn = "arn:aws:iam::123456789012:role/DataAnalystRole"
# database_name = "finance_db"
# table_name = "transactions"
# resource_column_names = [
#     "customer_id",
#     "amount",
#     "transaction_date",
# ]  # columns to allow
# data_filter_name = "TransactionsFilter"  # must be pre-created in Lake Formation


# # Step 1: Grant Column-Level Permissions
# def grant_column_permissions():
#     lakeformation_client.grant_permissions(
#         Principal={"DataLakePrincipalIdentifier": principal_arn},
#         Resource={
#             "TableWithColumns": {
#                 "DatabaseName": database_name,
#                 "Name": table_name,
#                 "ColumnNames": resource_column_names,
#             }
#         },
#         Permissions=["SELECT"],
#         PermissionsWithGrantOption=[],
#     )
#     print("✅ Granted column-level SELECT permissions.")


# # Step 2: Grant Row-Level Permissions (using data filter)
# def grant_row_level_permissions():
#     lakeformation_client.grant_permissions(
#         Principal={"DataLakePrincipalIdentifier": principal_arn},
#         Resource={
#             "DataCellsFilter": {
#                 "TableCatalogId": "123456789012",
#                 "DatabaseName": database_name,
#                 "TableName": table_name,
#                 "Name": data_filter_name,
#             }
#         },
#         Permissions=["SELECT"],
#         PermissionsWithGrantOption=[],
#     )
#     print("✅ Granted row-level SELECT permissions using Data Filter.")


# grant_column_permissions()
# grant_row_level_permissions()


#==============================================================================

if __name__ == "__main__":
    resources={
        'Catalog': {}
        ,
        'Database': {
            'CatalogId': 'string',
            'Name': 'string'
        },
        'Table': {
            'CatalogId': 'string',
            'DatabaseName': 'string',
            'Name': 'string',
            'TableWildcard': {}

        },
        'TableWithColumns': {
            'CatalogId': 'string',
            'DatabaseName': 'string',
            'Name': 'string',
            'ColumnNames': [
                'string',
            ],
            'ColumnWildcard': {
                'ExcludedColumnNames': [
                    'string',
                ]
            }
        },
        'DataLocation': {
            'CatalogId': 'string',
            'ResourceArn': 'string'
        },
        'DataCellsFilter': {
            'TableCatalogId': 'string',
            'DatabaseName': 'string',
            'TableName': 'string',
            'Name': 'string'
        },
        'LFTag': {
            'CatalogId': 'string',
            'TagKey': 'string',
            'TagValues': [
                'string',
            ]
        },
        'LFTagPolicy': {
            'CatalogId': 'string',
            'ResourceType': 'DATABASE'|'TABLE',
            'Expression': [
                {
                    'TagKey': 'string',
                    'TagValues': [
                        'string',
                    ]
                },
            ]
        }
    },

    permissions=['ALL'], # Other Options: 'SELECT', 'ALTER', 'DROP', 'DELETE', 'INSERT', 'DESCRIBE', 'CREATE_DATABASE', 'CREATE_TABLE', 'DATA_LOCATION_ACCESS', 'CREATE_LF_TAG', 'ASSOCIATE', 'GRANT_WITH_LF_TAG_EXPRESSION'
    grantable_permissions=['ALL'] # Other Options: 'SELECT', 'ALTER', 'DROP', 'DELETE', 'INSERT', 'DESCRIBE', 'CREATE_DATABASE', 'CREATE_TABLE', 'DATA_LOCATION_ACCESS', 'CREATE_LF_TAG', 'ASSOCIATE', 'GRANT_WITH_LF_TAG_EXPRESSION'

    grant_permissions(resources, permissions, grantable_permissions)
