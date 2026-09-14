import boto3
import botocore
from botocore.exceptions import ClientError
import os, time, json
from datetime import date


#=============================================================================
events_client        = boto3.client('events')

#=============================================================================

def create_eventbridge_schedule_rule(rule_name, schedule_expression, description=None):
    """
    Creates an AWS EventBridge rule with a schedule.

    Args:
        rule_name (str): The name of the rule.
        schedule_expression (str): The schedule expression in either `rate` or `cron` format.
            Example:
            - Rate: 'rate(5 minutes)'
            - Cron: 'cron(0 12 * * ? *)'
        description (str, optional): A description of the rule. Defaults to None.

    Returns:
        dict: Response from the AWS `put_rule` API call.
    """
    events_client = boto3.client('events')

    # Create the rule
    response = events_client.put_rule(
        Name=rule_name,
        ScheduleExpression=schedule_expression,
        State='ENABLED',  # Can also be 'DISABLED'
        Description=description or f"Schedule rule: {schedule_expression}"
    )

    print(f"Rule created with ARN: {response['RuleArn']}")
    return response

def delete_event_bridge_rule(rule_name, target_ids=[]):
    if not target_ids: target_ids = [f"{rule_name}_target"]
    # Step 1: Remove targets from the rule
    events_client.remove_targets(
        Rule=rule_name,
        Ids=target_ids  # List of target ids to remove
    )

    # Step 2: Delete the rule
    events_client.delete_rule(
        Name=rule_name,
        Force=True  # Optional. Set to True if you want to delete the rule even if it is still associated with targets.
    )

    print(f"Rule {rule_name} deleted successfully.")

def create_glue_job_eventbridge_rule(rule_name, job_name, target_arn, event_bus_name='default'):
    """
    Create an EventBridge rule to monitor a specific Glue job state changes and send notifications to the specified target.
    
    :param rule_name: Name of the EventBridge rule.
    :param job_name: Name of the Glue job to monitor.
    :param target_arn: ARN of the target (SNS topic, Lambda function).
    :param target_type: Type of the target ('sns' or 'lambda').
    :param event_bus_name: Name of the EventBridge event bus (default is 'default').
    :return: Response from EventBridge put_rule API call.
    """

    eventbridge_client = boto3.client('events')

    # Define the event pattern to monitor specific Glue job state changes
    event_pattern = {
        "source": ["aws.glue"],
        "detail-type": ["Glue Job State Change"],
        "detail": {
            "jobName": [job_name],
            "state": ["SUCCEEDED", "FAILED", "STOPPED"]
        }
    }

    # Create the EventBridge rule
    rule_response = eventbridge_client.put_rule(
        Name=rule_name,
        EventPattern=json.dumps(event_pattern),
        State='ENABLED',
        Description=f'Rule to capture AWS Glue job state changes for job: {job_name}',
        EventBusName=event_bus_name
    )
    
    # Define target settings (SNS or Lambda)
    target_id = f"{rule_name}-target"
    
    target_input = {
        'Arn': target_arn,
        'Id': target_id
    }
    
    # Add the target to the rule
    eventbridge_client.put_targets(
        Rule=rule_name,
        EventBusName=event_bus_name,
        Targets=[target_input]
    )

    return rule_response
