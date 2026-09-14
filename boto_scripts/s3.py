import os
from datetime import date
from dotenv import load_dotenv

import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from botocore.exceptions import NoCredentialsError, PartialCredentialsError


ACCOUNT_ID = os.environ['AWS_ACCOUNT_ID_ROOT']
REGION = os.environ['AWS_DEFAULT_REGION']
# =============================================================================
# Initialize a session using Amazon S3
s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')
# Load environment variables from the .env file
load_dotenv()
# =============================================================================

def create_s3_bucket(bucket_name, folders=[], region=REGION, enable_versioning=False, enable_encryption=False):
    """
    Create an S3 bucket with specified options and create folders within the bucket.

    :param bucket_name: Name of the S3 bucket to create.
    :param region: AWS region to create the bucket in.
    :param acl: Access control list (ACL) for the bucket. Default is 'private'.
    :param enable_versioning: Enable versioning for the bucket. Default is False.
    :param enable_encryption: Enable server-side encryption for the bucket. Default is False.
    :param folders: List of folder names to create within the bucket. Default is None.
    :raises ClientError: If there is an error creating the bucket.
    :raises NoCredentialsError: If credentials are not available.
    :raises PartialCredentialsError: If incomplete credentials are provided.
    """
    try:

        # Create the bucket
        if region:
            create_bucket_configuration = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(Bucket=bucket_name)
        
        print(f"Bucket '{bucket_name}' created successfully")

        # Enable versioning if specified
        if enable_versioning:
            s3_client.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            print(f"Versioning enabled for bucket '{bucket_name}'")

        # Enable server-side encryption if specified
        if enable_encryption:
            s3_client.put_bucket_encryption(
                Bucket=bucket_name,
                ServerSideEncryptionConfiguration={
                    'Rules': [
                        {
                            'ApplyServerSideEncryptionByDefault': {
                                'SSEAlgorithm': 'AES256'
                            }
                        }
                    ]
                }
            )
            print(f"Server-side encryption enabled for bucket '{bucket_name}'")

        # Create folders if specified
        if folders:
            for folder in folders:
                if not folder.endswith('/'): folder += '/'
                s3_client.put_object(Bucket=bucket_name, Key=folder)
                print(f"Folder '{folder}' created in bucket '{bucket_name}'")

    except ClientError as e:
        print(f"Error creating bucket or folders: {e}")
        raise
    except NoCredentialsError:
        print("Credentials not available")
        raise
    except PartialCredentialsError:
        print("Incomplete credentials provided")
        raise

def create_s3_bucket2(bucket_name, folders=[], region=REGION, acl='private', enable_versioning=False, enable_encryption=False):
    """
    Create an S3 bucket with specified options and create folders within the bucket.

    :param bucket_name: Name of the S3 bucket to create.
    :param region: AWS region to create the bucket in.
    :param acl: Access control list (ACL) for the bucket. Default is 'private'.
    :param enable_versioning: Enable versioning for the bucket. Default is False.
    :param enable_encryption: Enable server-side encryption for the bucket. Default is False.
    :param folders: List of folder names to create within the bucket. Default is None.
    :raises ClientError: If there is an error creating the bucket.
    :raises NoCredentialsError: If credentials are not available.
    :raises PartialCredentialsError: If incomplete credentials are provided.
    """
    try:

        # Create the bucket
        if region:
            create_bucket_configuration = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name, ACL=acl)
        else:
            s3_client.create_bucket(Bucket=bucket_name, ACL=acl)
        
        print(f"Bucket '{bucket_name}' created successfully")

        # Enable versioning if specified
        if enable_versioning:
            s3_client.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            print(f"Versioning enabled for bucket '{bucket_name}'")

        # Enable server-side encryption if specified
        if enable_encryption:
            s3_client.put_bucket_encryption(
                Bucket=bucket_name,
                ServerSideEncryptionConfiguration={
                    'Rules': [
                        {
                            'ApplyServerSideEncryptionByDefault': {
                                'SSEAlgorithm': 'AES256'
                            }
                        }
                    ]
                }
            )
            print(f"Server-side encryption enabled for bucket '{bucket_name}'")

        # Create folders if specified
        if folders:
            for folder in folders:
                if not folder.endswith('/'): folder += '/'
                s3_client.put_object(Bucket=bucket_name, Key=folder)
                print(f"Folder '{folder}' created in bucket '{bucket_name}'")

    except ClientError as e:
        print(f"Error creating bucket or folders: {e}")
        raise
    except NoCredentialsError:
        print("Credentials not available")
        raise
    except PartialCredentialsError:
        print("Incomplete credentials provided")
        raise

def delete_s3_bucket(bucket_name, region=REGION):
    """
    Delete an S3 bucket and all its contents.

    :param bucket_name: Name of the S3 bucket to delete.
    :param region: AWS region where the bucket is located.
    :raises ClientError: If there is an error deleting the bucket.
    :raises NoCredentialsError: If credentials are not available.
    :raises PartialCredentialsError: If incomplete credentials are provided.
    """
    try:

        bucket = s3_resource.Bucket(bucket_name)

        # Delete all objects in the bucket
        bucket.objects.delete()
        print(f"All objects in bucket '{bucket_name}' have been deleted.")

        # Delete the bucket itself
        s3_client.delete_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' deleted successfully.")

    except ClientError as e:
        print(f"Error deleting bucket: {e}")
        raise
    except NoCredentialsError:
        print("Credentials not available")
        raise
    except PartialCredentialsError:
        print("Incomplete credentials provided")
        raise

def upload_folder_to_s3(bucket_name, local_dir, s3_prefix=None, region=REGION):
    """
    Uploads the contents of a local folder (recursively) to an S3 bucket.

    Args:
        bucket_name (str): The name of the S3 bucket to upload files to.
        local_dir (str): The local path to the folder whose contents will be uploaded.
        s3_prefix (str, optional): The destination folder path in the S3 bucket.
            If specified, files will be uploaded under this prefix in the bucket.
        region (str, optional): AWS region where the bucket is located. Defaults to REGION.

    Notes:
        - All files in the folder and its subfolders will be uploaded.
        - The directory structure is preserved in the S3 bucket.
        - On Windows, backslashes in paths are replaced with forward slashes for S3 compatibility.

    Example:
        >>> upload_folder_to_s3("my-bucket", "./data", "backup/data")
        # Uploads all files from ./data to s3://my-bucket/backup/data/
    """
    s3_client = boto3.client("s3", region_name=region)

    # Traverse the directory
    for root, dirs, files in os.walk(local_dir):
        for file_name in files:
            # Full file path on local system
            file_path = os.path.join(root, file_name)

            # Calculate S3 key (i.e., path in the S3 bucket)
            if s3_prefix:  # if you want to upload inside a folder in the bucket
                s3_key = os.path.join(s3_prefix, os.path.relpath(file_path, local_dir))
            else:
                s3_key = os.path.relpath(file_path, local_dir)

            # Replace backslashes on Windows systems to avoid issues in S3
            s3_key = s3_key.replace("\\", "/")

            # Upload file to S3
            print(f"Uploading {file_path} to s3://{bucket_name}/{s3_key}")
            s3_client.upload_file(file_path, bucket_name, s3_key)

def upload_file_to_s3(bucket_name, lcl_file_path, object_name=None):
    """
    Uploads a file to an Amazon S3 bucket.

    This function uploads a local file to the specified S3 bucket. If no object name is provided, 
    the file name is used as the S3 object name.

    Args:
        bucket_name (str): The name of the S3 bucket where the file will be uploaded.
        lcl_file_path (str): The local path to the file to be uploaded.
        object_name (str, optional): The S3 object name. Defaults to None, in which case the file name is used.

    Returns:
        None

    Raises:
        FileNotFoundError: If the specified file does not exist.
        NoCredentialsError: If AWS credentials are not available.
        PartialCredentialsError: If incomplete AWS credentials are provided.

    Example:
        >>> upload_file_to_s3("my-bucket", "local-file.txt", "folder/remote-file.txt")
        File 'local-file.txt' uploaded to bucket 'my-bucket' as 'folder/remote-file.txt'

    Notes:
        - Ensure the `boto3` library is installed (`pip install boto3`).
        - Make sure the AWS credentials are correctly configured in your environment.
        - The `boto3.client('s3')` instance (`s3_client`) must be properly initialized before calling this function.
    """
    # If S3 object_name was not specified, use lcl_file_path
    if object_name is None:
        object_name = lcl_file_path

    try:
        response = s3_client.upload_file(lcl_file_path, bucket_name, object_name)
        print(f"File '{lcl_file_path}' uploaded to bucket '{bucket_name}' as '{object_name}'")
    except FileNotFoundError:
        print("The file was not found")
    except NoCredentialsError:
        print("Credentials not available")
    except PartialCredentialsError:
        print("Incomplete credentials provided")

# Function to delete a file from an S3 bucket
def delete_file_from_s3(bucket_name, object_name):

    try:
        response = s3_client.delete_object(Bucket=bucket_name, Key=object_name)
        print(f"File '{object_name}' deleted from bucket '{bucket_name}'")
    except NoCredentialsError:
        print("Credentials not available")
    except PartialCredentialsError:
        print("Incomplete credentials provided")


# =============================================================================
if __name__ == "__main__":

    bucket_name = 'EMR-' + date.today().strftime('%Y-%m-%d')  # The name must be unique across all of Amazon S3
    region = os.getenv('AWS_DEFAULT_REGION')    # Specify the AWS region, e.g., 'us-west-1'
    acl = 'private'                             # Set the ACL (e.g., 'private', 'public-read')
    enable_versioning = False                   # Enable versioning
    enable_encryption = False                   # Enable server-side encryption
    folders = ['input/', 'output/', 'logs/']    # List of folders to create

    create_s3_bucket(bucket_name, region, acl, enable_versioning, enable_encryption, folders)
    # delete_s3_bucket(bucket_name, region)
    
    file_name = os.environ['DATA'] + '/uspopulation.csv'  # The local file you want to upload
    folder_name = "input"
    object_name = f"{folder_name}/uspopulation.csv"  # The name to save the file as in the S3 bucket


    # Upload the file
    # upload_file_to_s3(bucket_name, file_name, object_name)

    # Delete the file
    # delete_file_from_s3(bucket_name, object_name)
