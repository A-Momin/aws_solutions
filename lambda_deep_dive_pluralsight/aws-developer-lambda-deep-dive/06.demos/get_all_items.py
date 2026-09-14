import boto3
import json
import decimal

dynamodb = boto3.resource('dynamodb')

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

def lambda_handler(event, context):
    table = dynamodb.Table('inventory')
    response = table.scan()
    
    return {
        "statusCode": 200,
        "body": json.dumps(response, cls=DecimalEncoder),
        "headers": {
            'Content-Type': 'application/json'
        }
    }
