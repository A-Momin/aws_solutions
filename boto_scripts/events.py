import boto3
import botocore
from botocore.exceptions import ClientError
import os, time, json, subprocess

import s3, iam, ec2, lambda_fn

events_client = boto3.client('events')

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
