# [Intro to Amazon EMR - Big Data Tutorial using Spark](https://www.youtube.com/watch?v=8bOgOvz6Tcg&t=667s)
### ===========================================================================

from datetime import date
import os
from s3 import create_s3_bucket, delete_s3_bucket
from s3 import upload_file_to_s3


# =============================================================================

if __name__ == "__main__":
    
    bucket_name = 'emr-' + date.today().strftime('%Y-%m-%d')  # The name must be unique across all of Amazon S3
    region = os.getenv('AWS_DEFAULT_REGION')    # Specify the AWS region, e.g., 'us-west-1'
    acl = 'private'                             # Set the ACL (e.g., 'private', 'public-read')
    enable_versioning = False                   # Enable versioning
    enable_encryption = False                   # Enable server-side encryption
    prefix = f"monthly-build/{date.today().strftime('%Y-%m-%d')}"
    folders = [f"{prefix}/input/", f"{prefix}/output/", f"{prefix}/logs/"]    # List of folders to create
    
    create_s3_bucket(bucket_name, region, acl, enable_versioning, enable_encryption, folders)
    # delete_s3_bucket(bucket_name, region)
    

    file_name1 = os.environ['DATA'] + '/restaurant_violations.csv'  # The local file you want to upload
    folder_name = f"{prefix}/input/"
    object_name1 = f"{folder_name}restaurant_violations.csv"  # The name to save the file as in the S3 bucket
    
    # Upload the file
    upload_file_to_s3(bucket_name, file_name1, object_name1)
    # delete_file_from_s3(bucket_name, object_name1)

    file_name2 = "/Users/am/mydocs/Software_Development/Web_Development/aws/scripts/emr_tutorial/main.py"
    object_name2 = f"{prefix}/main.py"  # The name to save the file as in the S3 bucket
    
    # Upload the file
    upload_file_to_s3(bucket_name, file_name2, object_name2)
    # delete_file_from_s3(bucket_name, object_name2)
