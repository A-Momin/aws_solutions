
import os
import boto3
from botocore.exceptions import ClientError

REGION = os.environ['AWS_DEFAULT_REGION']
glue_client = boto3.client('glue')
lakeformation_client = boto3.client('lakeformation')


def create_glue_data_catalog(
    catalog_name,
    description=None,
    parameters=None,
    target_database=None,
    target_table=None,
    target_path=None,
    storage_descriptor=None,
    table_type='EXTERNAL_TABLE',  # Other options: 'VIRTUAL_VIEW'
    partition_keys=None,
    view_expanded_text=None,
    view_original_text=None,
    owner=None,
    retention=None,
    last_access_time=None,
    last_analyzed_time=None,
    table_properties=None,
    classification=None,
    tags=None
    ):
    """
    Create a Glue Data Catalog with all available options and parameters with default values.

    :param catalog_name: The name of the data catalog.
    :param description: A description of the data catalog.
    :param parameters: A dictionary of parameters for the data catalog.
    :param target_database: The name of the target database.
    :param target_table: The name of the target table.
    :param target_path: The S3 path for the data.
    :param storage_descriptor: The storage descriptor object.
    :param table_type: The type of the table. Default is 'EXTERNAL_TABLE'.
    :param partition_keys: List of partition keys for the table.
    :param view_expanded_text: The expanded text of the view.
    :param view_original_text: The original text of the view.
    :param owner: The owner of the table.
    :param retention: The retention period for the table.
    :param last_access_time: The last access time of the table.
    :param last_analyzed_time: The last analyzed time of the table.
    :param table_properties: A dictionary of table properties.
    :param classification: The classification of the table.
    :param tags: Tags for the data catalog.
    :return: None
    """

    try:
        # Build the table input
        table_input = {
            'Name': catalog_name,
            'Description': description,
            'Parameters': parameters or {},
            'StorageDescriptor': storage_descriptor or {},
            'TableType': table_type,
            'PartitionKeys': partition_keys or [],
            'ViewExpandedText': view_expanded_text,
            'ViewOriginalText': view_original_text,
            'Owner': owner,
            'Retention': retention,
            'LastAccessTime': last_access_time,
            'LastAnalyzedTime': last_analyzed_time,
            'TableProperties': table_properties or {},
            'Classification': classification
        }

        # Filter out None values
        table_input = {k: v for k, v in table_input.items() if v is not None}

        # Create the table
        response = glue_client.create_table(
            DatabaseName=target_database,
            TableInput=table_input,
            Tags=tags or {}
        )

        print(f"Data catalog created successfully: {response}")

    except ClientError as e:
        print(f"Error creating data catalog: {e}")

def create_glue_crawler(crawler_name, role_arn, db_name, target={}, table_prefix=''):
    try:
        response = glue_client.create_crawler(
            Name=crawler_name,
            Role=role_arn, # or glue_role_name
            DatabaseName=db_name,
            Description='Crawler for generated Sales schema',
            Targets=target,
            TablePrefix=table_prefix,
            SchemaChangePolicy={
                'UpdateBehavior': 'UPDATE_IN_DATABASE',
                'DeleteBehavior': 'DELETE_FROM_DATABASE'
            },
            RecrawlPolicy={
                'RecrawlBehavior': 'CRAWL_EVERYTHING'
            },
            #,Configuration='{ "Version": 1.0, "CrawlerOutput": { "Partitions": { "AddOrUpdateBehavior": "InheritFromTable" } } }'
        )
        print(f"Successfully created Glue crawler: {crawler_name}")
        return response
    except Exception as e:
        print(f"Error creating Glue crawler {crawler_name}: {str(e)}")

def create_glue_jdbc_crawler(crawler_name, jdbc_connection_name, role_arn, db_name, target_path, table_prefix=''):
    try:
        response = glue_client.create_crawler(
            Name=crawler_name,
            Role=role_arn,
            DatabaseName=db_name,
            Targets={
                'JdbcTargets': [
                    {
                        'ConnectionName': jdbc_connection_name,
                        'Path': target_path,
                        'Exclusions': [],  # Optional: specify any patterns to exclude
                    }
                ]
            },
            SchemaChangePolicy={
                'UpdateBehavior': 'UPDATE_IN_DATABASE',
                'DeleteBehavior': 'DEPRECATE_IN_DATABASE'
            },
            TablePrefix=table_prefix
        )
        print(f"Successfully created Glue crawler: {crawler_name}")
    except Exception as e:
        print(f"Error creating Glue crawler {crawler_name}: {str(e)}")

def create_glue_s3_crawler(crawler_name, role_arn, db_name, target_path, table_prefix=''):
    try:
        response = glue_client.create_crawler(
            Name=crawler_name,
            Role=role_arn, # or glue_role_name
            DatabaseName=db_name,
            Description='Crawler for generated Sales schema',
            Targets={
                'S3Targets': [
                    {
                        'Path': target_path
                    },
                ]
            },
            TablePrefix=table_prefix,
            SchemaChangePolicy={
                'UpdateBehavior': 'UPDATE_IN_DATABASE',
                'DeleteBehavior': 'DELETE_FROM_DATABASE'
            },
            RecrawlPolicy={
                'RecrawlBehavior': 'CRAWL_EVERYTHING'
            },
            #,Configuration='{ "Version": 1.0, "CrawlerOutput": { "Partitions": { "AddOrUpdateBehavior": "InheritFromTable" } } }'
        )
        print(f"Successfully created Glue crawler: {crawler_name}")
    except Exception as e:
        print(f"Error creating Glue crawler {crawler_name}: {str(e)}")

def create_glue_job(job_name, script_location, role_arn, temp_dir, spark_event_log_path, number_of_workers=2, worker_type='G.1X'):
    try:
        response = glue_client.create_job(
            Name=job_name,
            Role=role_arn,
            ExecutionProperty={
                'MaxConcurrentRuns': 1
            },
            Command={
                'Name': 'glueetl',
                'ScriptLocation': script_location,
                'PythonVersion': '3'
            },
            DefaultArguments={
                '--TempDir': temp_dir,
                '--class': 'GlueApp',
                '--enable-continuous-cloudwatch-log': 'true',
                '--enable-glue-datacatalog': 'true',
                '--enable-metrics': 'true',
                '--enable-spark-ui': 'true',
                '--job-bookmark-option': 'job-bookmark-enable',
                '--job-language': 'python',
                '--spark-event-logs-path': spark_event_log_path
            },
            MaxRetries=0,
            Timeout=5,              # in minutes, max is 2,880 min (48 Hourse)
            GlueVersion='4.0',
            NumberOfWorkers=number_of_workers,
            WorkerType=worker_type  # Default worker type (Standard or G.1X, G.2X)

        )
        print(f"Glue Job {job_name} created successfully.")
    except Exception as e:
        print(f"Error creating Glue job {job_name}: {str(e)}")

def create_glue_job_v2(
    job_name,
    script_location,
    role_arn,
    default_args={},
    number_of_workers=2,
    worker_type="G.1X",
    glue_version="4.0",
    ):
    """
    Create an AWS Glue job with optional zipped external Python libraries.

    Args:
        job_name (str): Name of the Glue job.
        script_location (str): S3 path to the Glue ETL script.
        role_arn (str): IAM role ARN for the Glue job.
        temp_dir (str): Temporary directory path in S3.
        spark_event_log_path (str): S3 path for Spark event logs.
        number_of_workers (int, optional): Number of workers for the job. Default is 2.
        default_args (dict, optional): Additional default arguments for the Glue job.
        worker_type (str, optional): Type of worker to use. Default is 'G.1X'.
        external_lib_s3 (str, optional): S3 URI for zipped Python library to be used in the Glue job.

    Returns:
        dict: Response from AWS Glue API if the job is created successfully.

    Raises:
        Exception: If an error occurs during Glue job creation.
    """
    try:
        # Default arguments for the Glue job
        args = {
            "--class": "GlueApp",
            "--enable-continuous-cloudwatch-log": "true",
            "--enable-glue-datacatalog": "true",
            "--enable-metrics": "true",
            "--enable-spark-ui": "true",
            # "--library-path": f"s3://{lib_path}/",  # Path to external libraries (JARs, compiled libraries, JDBC drivers)
        }
        args.update(default_args)

        # Create the Glue job
        response = glue_client.create_job(
            Name=job_name,
            Role=role_arn,
            ExecutionProperty={"MaxConcurrentRuns": 1},
            Command={
                "Name": "glueetl",
                "ScriptLocation": script_location,
                "PythonVersion": "3",
            },
            DefaultArguments=args,  # Merge with any additional arguments
            MaxRetries=0,
            Timeout=5,  # in minutes, max is 2,880 min (48 Hours)
            GlueVersion=glue_version,
            NumberOfWorkers=number_of_workers,
            WorkerType=worker_type,  # can be 'Standard', 'G.1X', or 'G.2X'
            # ExecutionClass='STANDARD',    # Default execution class for Glue jobs (can be 'STANDARD' or 'FLEX')
            # MaxCapacity=10.0,             # Default maximum capacity for the Glue job
        )

        print(f"Glue Job {job_name} created successfully.")
        return response

    except Exception as e:
        print(f"Error creating Glue job {job_name}: {str(e)}")
        raise

def create_glue_connection(connection_name, jdbc_connection_url, username, password, security_group_id, subnet_id, region=REGION):
    """
    Creates an AWS Glue connection to an AWS MySQL RDS instance.
    
    :param connection_name: Name of the Glue connection
    :param db_name: Name of the database on the RDS instance
    :param db_instance_identifier: Identifier of the RDS instance
    :param username: Username to access the database
    :param password: Password to access the database
    :param security_group_id: Security group ID associated with the RDS instance
    :param subnet_id: Subnet ID associated with the RDS instance
    :param region: AWS region where the Glue connection will be created
    """
    
    # Construct the connection properties
    connection_properties = {
        'JDBC_CONNECTION_URL': jdbc_connection_url,
        'USERNAME': username,
        'PASSWORD': password,
        'JDBC_ENFORCE_SSL': 'false'  # set to 'true' if using SSL
    }
    
    # Construct the physical connection requirements
    physical_connection_requirements = {
        'SecurityGroupIdList': [security_group_id],
        'SubnetId': subnet_id
    }
    
    # Create the Glue connection
    response = glue_client.create_connection(
        ConnectionInput={
            'Name': connection_name,
            'ConnectionType': 'JDBC',
            'ConnectionProperties': connection_properties,
            'PhysicalConnectionRequirements': physical_connection_requirements
        }
    )
    
    return response

def test_glue_connection(connection_name):
    glue_client = boto3.client('glue', region_name=REGION)  # Change region as needed
    try:
        # Start the connection test
        response = glue_client.start_connection_test(ConnectionName=connection_name)
        print(f"Started connection test for '{connection_name}'.")

        # Retrieve the test result
        test_status = response.get('Status', 'UNKNOWN')
        print(f"Test status: {test_status}")

        return response
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityNotFoundException':
            print(f"Connection '{connection_name}' not found.")
        else:
            print(f"An error occurred: {e}")
        return None

def start_glue_job(job_name, arguments=None):
    glue_client = boto3.client('glue', region_name=REGION)  # Change region accordingly
    try:
        # Start the Glue job
        response = glue_client.start_job_run(
            JobName=job_name,
            Arguments=arguments or {}
        )
        
        job_run_id = response['JobRunId']
        print(f"Started job '{job_name}' with JobRunId: {job_run_id}")
        return job_run_id
    except ClientError as e:
        print(f"An error occurred: {e}")
        return None

def get_job_run_status(job_name, job_run_id):
    try:
        response = glue_client.get_job_run(JobName=job_name, RunId=job_run_id)
        status = response['JobRun']['JobRunState']
        print(f"JobRunId {job_run_id} status: {status}")
        return status
    except ClientError as e:
        print(f"An error occurred: {e}")
        return None


if __name__ == "__main__":
    create_glue_data_catalog(
        catalog_name='my-catalog',
        description='A description for my data catalog',
        parameters={'param1': 'value1'},
        target_database='my_database',
        target_table='my_table',
        target_path='s3://my-bucket/my-data/',
        storage_descriptor={
            'Columns': [
                {'Name': 'column1', 'Type': 'string'},
                {'Name': 'column2', 'Type': 'int'}
            ],
            'Location': 's3://my-bucket/my-data/',
            'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
            'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
            'Compressed': False,
            'NumberOfBuckets': -1,
            'SerdeInfo': {
                'SerializationLibrary': 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe',
                'Parameters': {
                    'serialization.format': '1'
                }
            },
            'BucketColumns': [],
            'SortColumns': [],
            'Parameters': {},
            'SkewedInfo': {
                'SkewedColumnNames': [],
                'SkewedColumnValues': [],
                'SkewedColumnValueLocationMaps': {}
            },
            'StoredAsSubDirectories': False
        },
        table_type='EXTERNAL_TABLE',  # Other options: 'VIRTUAL_VIEW'
        partition_keys=[
            {'Name': 'year', 'Type': 'int'},
            {'Name': 'month', 'Type': 'int'}
        ],
        view_expanded_text=None,
        view_original_text=None,
        owner='owner_name',
        retention=0,
        last_access_time=None,
        last_analyzed_time=None,
        table_properties={'classification': 'csv'},
        classification='csv',
        tags={'Environment': 'Production'}
    )

    # Example usage
    response = create_glue_connection(
        connection_name='my-glue-connection',
        db_name='mydatabase',
        db_instance_identifier='mydbinstance',
        username='myusername',
        password='mypassword',
        security_group_id='sg-0123456789abcdef0',
        subnet_id='subnet-0123456789abcdef0',
        region=REGION
    )

    print(response)

