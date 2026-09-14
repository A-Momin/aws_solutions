import boto3
import json
import decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('inventory')

def get_item_quantity(itemId):
    response = table.get_item(Key = {'product_id': itemId})
    return int(response['Item']['quantity'])

def update_item_quantity(itemId, newQuantity):
    table.update_item(
            Key = {
                'product_id': itemId
            },
            UpdateExpression="set quantity=:q",
            ExpressionAttributeValues={
                ':q': int(newQuantity)
            },
            ReturnValues="NONE"
        )

def lambda_handler(event, context):
    itemId = event["itemId"]
    quantitypurchased = int(event["quantitypurchased"])
    
    availableQuantity = get_item_quantity(itemId)
    
    remainingItems = availableQuantity - quantitypurchased
    
    if remainingItems >= 0:
        update_item_quantity(itemId, remainingItems)
        
    return remainingItems