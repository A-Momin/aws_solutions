import boto3
import botocore
import json
import os
from misc import load_from_yaml, save_to_yaml

## ============================================================================

CONFIG_PATH = 'service_resources.yml'
CONFIG = load_from_yaml(CONFIG_PATH)

# Initialize the SQS client
sqs_client = boto3.client('sqs')
attributes = {
    'DelaySeconds': '0',
    'MaximumMessageSize': '262144',  # 256 KB
    'MessageRetentionPeriod': '345600',  # 4 days
    'ReceiveMessageWaitTimeSeconds': '0',
    'VisibilityTimeout': '30',
    'RedrivePolicy': json.dumps({
        'deadLetterTargetArn': 'arn:aws:sqs:us-east-1:123456789012:MyDeadLetterQueue',
        'maxReceiveCount': '5'
    }),
    'KmsMasterKeyId': 'alias/aws/sqs',
    'KmsDataKeyReusePeriodSeconds': '300',
    'FifoQueue': 'false',  # Set to 'true' if creating a FIFO queue
    'ContentBasedDeduplication': 'false'  # Set to 'true' if creating a FIFO queue with content-based deduplication
}

def create_sqs_queue(queue_name, attributes=attributes):
    """
    Creates an SQS queue with specified attributes.

    Parameters:
    queue_name (str): The name of the SQS queue.
    attributes (dict): A dictionary of attributes to set for the queue.

    Returns:
    dict: Response from the create_queue call.
    """
    # Initialize the SQS client
    sqs_client = boto3.client('sqs')

    try:
        # Create the SQS queue with the specified attributes
        response = sqs_client.create_queue(
            QueueName=queue_name,
            Attributes=attributes
        )
        print(f"Queue '{queue_name}' created successfully.")
        return response

    except sqs_client.exceptions.QueueNameExists:
        print(f"Queue '{queue_name}' already exists.")
    except Exception as e:
        print(f"An error occurred: {e}")

def send_message_to_sqs_queue(queue_url, message_body, message_attributes=None):
    """
    Send a message to an SQS queue.
    
    :param queue_url: The URL of the SQS queue
    :param message_body: The body of the message
    :param message_attributes: Additional attributes for the message (optional)
    :return: The ID of the sent message
    """
    try:
        response = sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=message_body,
            MessageAttributes=message_attributes or {}
        )
        message_id = response['MessageId']
        print(f"Sent message to queue {queue_url}. Message ID: {message_id}")
        return message_id
    except ClientError as e:
        print(f"Error sending message to SQS queue: {e}")
        return None

def receive_messages_from_sqs_queue(queue_url, max_number_of_messages=1, wait_time_seconds=0):
    """
    Receive messages from an SQS queue.
    
    :param queue_url: The URL of the SQS queue
    :param max_number_of_messages: The maximum number of messages to receive
    :param wait_time_seconds: The duration (in seconds) for which the call waits for a message to arrive in the queue
    :return: The received messages
    """
    try:
        response = sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=max_number_of_messages,
            WaitTimeSeconds=wait_time_seconds
        )
        messages = response.get('Messages', [])
        print(f"Received {len(messages)} messages from queue {queue_url}.")
        return messages
    except ClientError as e:
        print(f"Error receiving messages from SQS queue: {e}")
        return []

def delete_message_from_sqs_queue(queue_url, receipt_handle):
    """
    Delete a message from an SQS queue.
    
    :param queue_url: The URL of the SQS queue
    :param receipt_handle: The receipt handle of the message to delete
    """
    try:
        sqs_client.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )
        print(f"Deleted message from queue {queue_url}.")
    except ClientError as e:
        print(f"Error deleting message from SQS queue: {e}")

def delete_sqs_queue(queue_url):
    """
    Delete an SQS queue.
    
    :param queue_url: The URL of the SQS queue to delete
    """
    try:
        sqs_client.delete_queue(QueueUrl=queue_url)
        print(f"Deleted SQS queue with URL: {queue_url}")
    except ClientError as e:
        print(f"Error deleting SQS queue: {e}")

def create_all_sqs():
    # Example usage
    queue_name = 'OrdersQueue'
    message_body = 'This is a SQS test message'
    message_attributes = {
        'Author': {
            'StringValue': 'James',
            'DataType': 'String'
        },
        'Timestamp': {
            'StringValue': '2024-06-03T12:00:00Z',
            'DataType': 'String'
        }
    }

    # Create an SQS queue
    queue_url = create_sqs_queue(queue_name, attributes={
        'DelaySeconds': '5',
        'MessageRetentionPeriod': '86400'  # 1 day
    })

    if queue_url:
        # Send a message to the SQS queue
        message_id = send_message_to_sqs_queue(queue_url, message_body, message_attributes)

        # Receive messages from the SQS queue
        messages = receive_messages_from_sqs_queue(queue_url, max_number_of_messages=10, wait_time_seconds=10)

        # Process and delete received messages
        for message in messages:
            print(f"Message: {message['Body']}")
            delete_message_from_sqs_queue(queue_url, message['ReceiptHandle'])

            CONFIG['sqs']['queue_url'] = queue_url
            save_to_yaml(CONFIG_PATH, CONFIG)

if __name__ == "__main__":
    create_all_sqs()
    # # Clean up by deleting the SQS queue
    # queue_url = CONFIG['sqs']['queue_url']
    # delete_sqs_queue(queue_url)
