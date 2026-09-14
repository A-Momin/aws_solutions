def lambda_handler(event, context):
    print("=="*5 + "START EXECUTING THE LAMBDA" + "=="*5)
    print(event)
    print("=="*5 + "END EXECUTING THE LAMBDA" + "=="*5)
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }