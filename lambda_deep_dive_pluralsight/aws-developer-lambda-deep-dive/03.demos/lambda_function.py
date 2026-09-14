import boto3
import logging

client = boto3.client('dynamodb')
logger = logging.getLogger();
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info('Function:{} has started'.format(context.function_name))
    print('this is a simple log')
    client.create_backup(
        TableName='inventory',
        BackupName='MyAutomaticBackup'
        )