### S3 Uploads

-   [`aws s3`](https://docs.aws.amazon.com/cli/latest/reference/s3/index.html)

-   When you open up your demos file you'll see a templates folder. Along with licence information are three modified html email templates. Each template is ready to use with Jinja2 but we'll need to move it to an S3 bucket. Keep in mind that bucket names are **globall** unique. Meaning you can't use mine! Replace `gpc-cuckoo-bucket` with your bucket name. Also use the region you've been using throughout the course. The `\` character is to escape line breaks and make the code more readable.

-   Create a bucket with the AWS CLI:

    -   `$ aws s3 mb s3://gpc-cuckoo-bucket`
    -   `$ aws s3 ls` → Confirm the bucket was created

-   Upload the templates to your s3 bucket. Make sure you're in the `/templates` folder in your terminal first.

    -   `$ aws s3 cp ./templates s3://gpc-cuckoo-bucket --recursive` → Recursively copy `./template` into s3 bucket.
    -   `$ aws s3 ls gpc-cuckoo-bucket` → Confirm the files were moved to s3

-   Notes:

    -   Keep in mind that Lambda `cron()` scheduling is done on `UTC`.
    -   To get a cron expression in your timezone you may need to change the values
    -   7am EST - cron(0 12 ? _ MON-FRI _)
    -   Noon EST - cron(0 17 ? _ MON-FRI _)
    -   5pm EST - cron(0 22 ? _ MON-FRI _)
    -   Keep in mind time zone differences like Daylight Savings!

### Test it Locally before Deployment:

-   Create a virtual Environment and install follwoing in the environement.

    -   `$ python -m venv .venv`
    -   `$ source .venv/bin/activate`
    -   `$ pip install boto3`
    -   `$ pip install Jinja2`
    -   `$ python`

-   Enable Python shell

    -   `$ python`

    ```python
    >>> from cuckoo import *
    >>> event = {
        "id": "cdc73f9d-aea9-11e3-9d5a-835b769c0d9c",
        "detail-type": "Scheduled Event",
        "source": "aws.events",
        "account": "123456789012",
        "time": "1970-01-01T00:00:00Z",
        "region": "us-east-1",
        "resources": ["arn:aws:events:us-east-1:123456789012:rule/pickup"],
        "detail": {}
    }
    >>> handler(event, "")
    ```

---

### Setup and Prepare for Deployment

To take a look at creating our function package locally you can open the `setup.sh` file in a text editor.
Deploying your function with the AWS CLI. First make sure you've created your zip function package and you're in the same directory as that package.zip file.

#### Create IAM Role using IAM Management Console

-   AIM (Management Console) -> Roles -> Create Role -> Use Case : Lambda -> Next
    -> Search : SES -> Select : AmazonSESFullAccess - AWS Managed
    -> Search : S3 -> Select : AmazonS3FullAccess - AWS Managed
    -> Search : Lambda -> Select : AWSLambdaBasicExecutionRole - AWS managed
    -> Role Name : gpc_cuckoo_role -> Create Role.

-   Then list the roles on your account. We'll need to look for the role we created for this function earlier

    -   `$ aws iam list-roles`

        -   We'll see something like `arn:aws:iam::444510800003:role/gpc_cuckoo_role` in the output.
        -   Copy that role ARN because you'll need to replace the value after --role in the below command.

#### Create the Lambda function

```bash
aws lambda create-function \
    --function-name gpc_cuckoo \
    --runtime python3.7 \
    --role arn:aws:iam::583847744398:role/gpc_cuckoo_role \
    --handler cuckoo.handler \
    --zip-file fileb://./package.zip
```

-   Returned:

    ```json
    {
        "FunctionName": "gpc_cuckoo",
        "FunctionArn": "arn:aws:lambda:us-east-1:583847744398:function:gpc_cuckoo",
        "Runtime": "python3.7",
        "Role": "arn:aws:iam::583847744398:role/gpc_cuckoo_role",
        "Handler": "cuckoo.handler",
        "CodeSize": 335883,
        "Description": "",
        "Timeout": 3,
        "MemorySize": 128,
        "LastModified": "2022-12-23T06:03:52.833+0000",
        "CodeSha256": "1eGWUvw0aiK3fijQDwAHjT/N3OLD9CeXCwt2rwHwIz8=",
        "Version": "$LATEST",
        "TracingConfig": {
            "Mode": "PassThrough"
        },
        "RevisionId": "4c918435-b82a-4a9c-83c1-5b9a88d415de",
        "State": "Pending",
        "StateReason": "The function is being created.",
        "StateReasonCode": "Creating",
        "PackageType": "Zip",
        "Architectures": ["x86_64"],
        "EphemeralStorage": {
            "Size": 512
        },
        "SnapStart": {
            "ApplyOn": "None",
            "OptimizationStatus": "Off"
        }
    }
    ```

-   How to remove the Lambda Function?
    -   `$ aws lambda delete-function --function-name gpc_cuckoo`

#### Add permissions to the Lambda function

We'll have the function trust events from each of these Cloudwatch Events.

-   [`aws lambda`](https://docs.aws.amazon.com/cli/latest/reference/lambda/index.html#cli-aws-lambda)

```bash
aws lambda add-permission \
    --function-name gpc_cuckoo \
    --statement-id 1 \
    --action 'lambda:InvokeFunction' \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:us-east-1:583847744398:rule/pickup
    # --source-arn arn:aws:events:us-east-1:444510800003:rule/pickup
```

-   Returned:

    ```json
    {
        "Statement": {
            "Sid": "1",
            "Effect": "Allow",
            "Principal": {
                "Service": "events.amazonaws.com"
            },
            "Action": "lambda:InvokeFunction",
            "Resource": "arn:aws:lambda:us-east-1:583847744398:function:gpc_cuckoo",
            "Condition": {
                "ArnLike": {
                    "AWS:SourceArn": "arn:aws:events:us-east-1:583847744398:rule/pickup"
                }
            }
        }
    }
    ```

```bash
aws lambda add-permission \
 --function-name gpc_cuckoo \
 --statement-id 2 \
 --action 'lambda:InvokeFunction' \
 --principal events.amazonaws.com \
 --source-arn arn:aws:events:us-east-1:583847744398:rule/daily_tasks
 # --source-arn arn:aws:events:us-east-1:444510800003:rule/daily_tasks
```

-   Returned:

    ```json
    {
        "Statement": {
            "Sid": "2",
            "Effect": "Allow",
            "Principal": {
                "Service": "events.amazonaws.com"
            },
            "Action": "lambda:InvokeFunction",
            "Resource": "arn:aws:lambda:us-east-1:583847744398:function:gpc_cuckoo",
            "Condition": {
                "ArnLike": {
                    "AWS:SourceArn": "arn:aws:events:us-east-1:583847744398:rule/daily_tasks"
                }
            }
        }
    }
    ```

```bash
aws lambda add-permission \
 --function-name gpc_cuckoo \
 --statement-id 3 \
--action 'lambda:InvokeFunction' \
--principal events.amazonaws.com \
--source-arn arn:aws:events:us-east-1:583847744398:rule/come_to_work
```

-   Returned:

    ```json
    {
        "Statement": {
            "Sid": "3",
            "Effect": "Allow",
            "Principal": { "Service": "events.amazonaws.com" },
            "Action": "lambda:InvokeFunction",
            "Resource": "arn:aws:lambda:us-east-1:583847744398:function:gpc_cuckoo",
            "Condition": {
                "ArnLike": {
                    "AWS:SourceArn": "arn:aws:events:us-east-1:583847744398:rule/come_to_work"
                }
            }
        }
    }
    ```

#### Create Events (EventBridge) rules:

-   [`aws events`](https://docs.aws.amazon.com/cli/latest/reference/events/index.html)

```bash
aws events put-rule \
    --name come_to_work \
    --schedule-expression 'cron(0 12 ? * MON-FRI *)'

aws events put-rule \
    --name daily_tasks \
    --schedule-expression 'cron(0 17 ? * MON-FRI *)'

aws events put-rule \
    --name pickup \
    --schedule-expression 'cron(0 22 ? * MON-FRI *)'
```

-   `$ aws events list-rules` → List events

#### Add the Targets to AWS CloudWatch Events rule.

```bash
aws events put-targets \
    --rule pickup \
    --targets '{"Id" : "1", "Arn": "arn:aws:lambda:us-east-1:583847744398:function:gpc_cuckoo"}'

aws events put-targets \
    --rule daily_tasks \
    --targets '{"Id" : "2", "Arn": "arn:aws:lambda:us-east-1:583847744398:function:gpc_cuckoo"}'

aws events put-targets \
    --rule come_to_work \
    --targets '{"Id" : "3", "Arn": "arn:aws:lambda:us-east-1:583847744398:function:gpc_cuckoo"}'
```

#### Test the Lambda Function locally

-   With the events created make sure to modify your code skeleton. Come back for these commands when you need to test locally
-   Testing the function from the command line: (Make sure you're in the directory with the cuckoo.py file)
-   Call the handler function and give it a sample event. This event can either be the event ARN text or something else that contains text that contains some of the text that the function is looking for. The text should contain `come_to_work` or `daily_tasks` or `pickup`. We'll also put them into the following format to match the way they will be passed to the function by the AWS event

-   `$ python3` → Return python shell

    ```python
    >>> import cuckoo
    >>> cuckoo.handler({'resources':['some text containing the word pickup']},'context')
    >>> cuckoo.handler({'resources':['arn:aws:events:us-east-1:444510800003:rule/come_to_work']}, 'context')
    >>> cuckoo.handler({'resources':['a great daily_tasks test']},'context')
    ```

    -   If successful you won't see any output so check your email for the results!
