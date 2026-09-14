import boto3
import os, json, zipfile, io, time, shutil, subprocess
from io import BytesIO
from pathlib import Path


ACCOUNT_ID = os.environ['AWS_ACCOUNT_ID_ROOT']
REGION = os.environ['AWS_DEFAULT_REGION']
VPC_ID = 'vpc-03617a8a518caa526'
DEFAULT_SUBNET_IDS = ['subnet-0980ad10eb313405b', 'subnet-0de97821ddb8236f7', 'subnet-0a160fbe0fcafe373', 'subnet-0ca765b361e4cb186', 'subnet-0a972b05a5b162feb']
SUBNET_ID = DEFAULT_SUBNET_IDS[0]
DEFAULT_SECURITY_GROUP_ID = 'sg-07f4ccd7a5be677ea'


kinesis_client = boto3.client("kinesis")


#==============================================================================
def create_kinesis_data_stream(
    stream_name,
    shard_count=1,
    stream_mode="ON_DEMAND",
    tags=None,
    encryption_type="NONE",
    kms_key_id=None,
    retention_period_hours=24,
):
    """
    Create an AWS Kinesis Data Stream with the specified options.

    Parameters:
        stream_name (str): Name of the stream to be created.
        shard_count (int): Number of shards (required for provisioned mode, default: 1).
        stream_mode (str): Stream mode - "PROVISIONED" or "ON_DEMAND" (default: "ON_DEMAND").
        tags (dict): Key-value pairs to tag the stream (default: None).
        encryption_type (str): "NONE" or "KMS" (default: "NONE").
        kms_key_id (str): KMS key ID for server-side encryption (default: None).
        retention_period_hours (int): Retention period in hours (default: 24).

    Returns:
        response (dict): Response from the create_stream API call.
    """
    # Initialize boto3 client for Kinesis

    # Build the stream creation parameters
    stream_params = {
        "StreamName": stream_name,
        "StreamModeDetails": {"StreamMode": stream_mode},
    }

    # Add shard count for provisioned mode
    if stream_mode == "PROVISIONED":
        stream_params["ShardCount"] = shard_count

    # Add encryption configuration if specified
    if encryption_type == "KMS" and kms_key_id:
        stream_params["StreamEncryption"] = {
            "EncryptionType": "KMS",
            "KeyId": kms_key_id,
        }

    # Add tags if specified
    if tags:
        stream_params["Tags"] = tags

    # Create the stream
    response = kinesis_client.create_stream(**stream_params)

    # Update retention period if necessary
    if retention_period_hours != 24:
        kinesis_client.increase_stream_retention_period(
            StreamName=stream_name,
            RetentionPeriodHours=retention_period_hours,
        )

    return response

# Example usage
if __name__ == "__main__":
    stream_name = "MyKinesisStream"

    # response = create_kinesis_data_stream(
    #     stream_name=stream_name,
    #     shard_count=2,
    #     stream_mode="PROVISIONED",
    #     tags={"Environment": "Development", "Project": "Example"},
    #     encryption_type="KMS",
    #     kms_key_id="arn:aws:kms:us-east-1:123456789012:key/example-key-id",
    #     retention_period_hours=48,
    # )

    # print("Stream created successfully:", response)
