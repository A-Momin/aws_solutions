import json
import boto3
import os
import decimal

sns = boto3.client('sns')

def lambda_handler(event, context):
    snsArn = os.environ['sns_arn']
    
    itemId = event["itemId"]
    neededQuantity = int(event["remainingItems"]) * -1
    
    print("sending message to: " + snsArn)
            
    message = "We need at least " + str(neededQuantity) + " more of item " + itemId
            
    response = sns.publish(
        TargetArn=snsArn,
        Message=json.dumps({
            'default': json.dumps(message)
        }),
        
        MessageStructure='json'
    )
