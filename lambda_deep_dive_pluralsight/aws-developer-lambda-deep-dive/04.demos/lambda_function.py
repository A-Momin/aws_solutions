import json
import boto3
import urllib.parse
import csv
from io import StringIO

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    print("Recived event: " + json.dumps(event))

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
     
    response = s3.get_object(Bucket=bucket, Key=key)
    text = response['Body'].read().decode('utf-8')
     
    print("Text in file: " + text)
     
    buff = StringIO(text)
    reader = csv.DictReader(buff)
     
    table = dynamodb.Table('inventory')

    for row in reader:
        table.put_item(
            Item={
                'product_id': row['Id'],
                'product_name': row['Name'],
                'price': row['Price'],
                'quantity': 0
            })