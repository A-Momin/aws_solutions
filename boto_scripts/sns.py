import boto3
import botocore
import json
import os
from misc import load_from_yaml, save_to_yaml

## ============================================================================


# Initialize boto3 clients
sns_client = boto3.client('sns')
attributes = {
    'DisplayName': 'My SNS Topic',
    'Policy': json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"AWS": "*"},
            "Action": "SNS:Publish",
            "Resource": "*"
        }]
    }),
    'DeliveryPolicy': json.dumps({
        "http": {
            "defaultHealthyRetryPolicy": {
                "numRetries": 3,
                "numMaxDelayRetries": 0,
                "numNoDelayRetries": 0,
                "numMinDelayRetries": 1,
                "backoffFunction": "linear"
            },
            "disableSubscriptionOverrides": False
        }
    }),
    'KmsMasterKeyId': 'alias/aws/sns',
    'TracingConfig': 'Active'
}


def create_sns_topic(topic_name, attributes={}):
    """
    Creates an SNS topic with specified attributes.

    Parameters:
    topic_name (str): The name of the SNS topic.
    attributes (dict): A dictionary of attributes to set for the topic.

    Returns:
    dict: Response from the create_topic call.
    """
    # Initialize the SNS client
    sns_client = boto3.client('sns')

    try:
        # Create the SNS topic
        response = sns_client.create_topic(
            Name=topic_name
        )
        topic_arn = response['TopicArn']

        # Set topic attributes
        for key, value in attributes.items():
            sns_client.set_topic_attributes(
                TopicArn=topic_arn,
                AttributeName=key,
                AttributeValue=value
            )
        
        print(f"Topic '{topic_name}' created successfully with ARN: {topic_arn}")
        return topic_arn

    except Exception as e:
        print(f"An error occurred: {e}")

def subscribe_to_sns_topic(topic_arn, protocol, endpoint):
    """
    Subscribe to an SNS topic.
    
    :param topic_arn: The ARN of the SNS topic
    :param protocol: The protocol to use (e.g., 'email', 'sms', 'sqs', etc.)
    :param endpoint: The endpoint to receive notifications (e.g., email address, phone number, etc.)
    """
    response = sns_client.subscribe(
        TopicArn=topic_arn,
        Protocol=protocol,
        Endpoint=endpoint
    )
    subscription_arn = response['SubscriptionArn']
    print(f"Subscribed to topic {topic_arn} with {protocol} endpoint {endpoint}. Subscription ARN: {subscription_arn}")
    return subscription_arn

def publish_message_to_sns_topic(topic_arn, message, subject=None):
    """
    Publish a message to an SNS topic.
    
    :param topic_arn: The ARN of the SNS topic
    :param message: The message to publish
    :param subject: The subject of the message (optional)
    """
    response = sns_client.publish(
        TopicArn=topic_arn,
        Message=message,
        Subject=subject
    )
    message_id = response['MessageId']
    print(f"Published message to topic {topic_arn}. Message ID: {message_id}")
    return message_id

def unsubscribe_from_sns_topic(topic_arn):

   # Step 1: List all subscriptions for the topic to find the Subscription ARN
    subscriptions = sns_client.list_subscriptions_by_topic(TopicArn=topic_arn)


    # Iterate over subscriptions and unsubscribe each
    for subscription in subscriptions['Subscriptions']:
        subscription_arn = subscription['SubscriptionArn']
        
        # if subscription_arn != 'PendingConfirmation':  # Ensure the subscription is active
        #     # Step 2: Unsubscribe each subscription
        response = sns_client.unsubscribe(SubscriptionArn=subscription_arn)
        print(f"Unsubscribed from {subscription_arn}")

def delete_sns_topic(topic_arn):
    """
    Delete an SNS topic.
    
    :param topic_arn: The ARN of the SNS topic to delete
    """
    unsubscribe_from_sns_topic(topic_arn=topic_arn)

    # Delete the SNS topic
    response = sns_client.delete_topic(TopicArn=topic_arn)
    print(f"Deleted SNS topic: {topic_arn}")


def create_all_sns():

    # Example usage
    topic_name = 'NotifyCourier'
    protocol = 'email'  # Change to 'sms' or 'sqs' as needed
    endpoint = 'BBCRedCap3@gmail.com'  # Change to phone number or SQS queue URL as needed
    message = 'This is a test message'
    subject = 'Test SNS Subject'

    # Create an SNS topic
    topic_arn = create_sns_topic(topic_name)

    # Subscribe to the SNS topic
    # subscription_arn = subscribe_to_sns_topic(topic_arn, protocol, endpoint)

    # Publish a message to the SNS topic
    message_id = publish_message_to_sns_topic(topic_arn, message, subject)



if __name__ == "__main__":
    pass

    # create_all_sns()
    # # Clean up by deleting the SNS topic
    # topic_arn = CONFIG['sns']['topic_arn']
    # delete_sns_topic(topic_arn)
