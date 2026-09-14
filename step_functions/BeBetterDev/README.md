-   [Build a Serverless Workflow with AWS Step Functions](https://www.youtube.com/watch?v=DFSko_sLyMM&list=PL9nWRykSBSFgQrO66TmO1vHFP6yuPF5G-&index=13)

    -   [CODE](./transaction_process.py)

-   [How to Start an AWS Step Function Workflow From Lambda | STEP BY STEP GUIDE](https://www.youtube.com/watch?v=kpuqc_7DQZA&list=PL9nWRykSBSFgQrO66TmO1vHFP6yuPF5G-&index=6)

    -   [CODE]

        ```python
        # lambda function
        import json
        import boto3
        import uuid

        client = boto3.client('stepfunctions')

        def lambda_handler(event, context):
            #INPUT -> { "TransactionId": "foo", "Type": "PURCHASE"}
            transactionId = str(uuid.uuid1()) #90a0fce-sfhj45-fdsfsjh4-f23f

            input = {'TransactionId': transactionId, 'Type': 'PURCHASE'}

            response = client.start_execution(
                stateMachineArn='YOUR ARN HERE!',
                name=transactionId,
                input=json.dumps(input)
            )
        ```
