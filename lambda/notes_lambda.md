### [Video Tutorials](https://www.youtube.com/playlist?list=PL9nWRykSBSFjodfc8l8M8yN0ieP94QeEL)

<details><summary ><a style="font-size:20px;color:Orange;text-align:left" href="https://www.youtube.com/playlist?list=PL9nWRykSBSFjodfc8l8M8yN0ieP94QeEL">AWS Lambda - Everything you need to know about Lambdas!</a></summary>

#### [AWS SQS to Lambda Tutorial in NodeJS | Step by Step](https://www.youtube.com/watch?v=JJQrVBRzlPg&list=PL9nWRykSBSFjodfc8l8M8yN0ieP94QeEL&index=3)

-   [PDF: AWS SQS to Lambda](./lambda_sqs.pdf)

#### [How to download a S3 File from Lambda in Python | Step by Step Guide](https://www.youtube.com/watch?v=6LvtSmJhVRE&list=PL9nWRykSBSFjodfc8l8M8yN0ieP94QeEL&index=10)

</details>

---

<details><summary style="font-size:20px;color:Orange;text-align:left">Interview Questions</summary>

1. <b style="color:magenta">What is AWS Lambda?</b>

    - AWS Lambda is a serverless computing service provided by Amazon Web Services. It allows you to run code without provisioning or managing servers. You can upload your code, and Lambda automatically takes care of scaling, monitoring, and maintaining the compute fleet needed to run your code.

2. <b style="color:magenta">How does AWS Lambda differ from traditional server-based computing?</b>

    - In traditional server-based computing, you need to provision and manage servers to host your application, and you pay for those servers whether they are actively processing requests or not. With AWS Lambda, you don't need to manage servers. The service automatically scales to handle the number of incoming requests and charges you only for the compute time consumed.

3. <b style="color:magenta">What are the key components of AWS Lambda?</b>

    - The key components of AWS Lambda include:

        - `Function`: The piece of code you want to run.
        - `Event Source`: AWS service or developer-created application that produces events to trigger a Lambda function.
        - `Execution Role`: The AWS Identity and Access Management (IAM) role that grants permissions to your Lambda function.

4. <b style="color:magenta">How does AWS Lambda pricing work?1. </b>

    - AWS Lambda pricing is based on the number of requests for your functions and the time your code executes. You are charged based on the number of requests and the duration your code runs in 100ms increments. There are no charges when your code is not running.

5. <b style="color:magenta">What are the supported languages for AWS Lambda functions?</b>

    - AWS Lambda supports a variety of programming languages, including Node.js, Python, Ruby, Java, Go, .NET Core, and custom runtime environments using the Runtime API.

6. <b style="color:magenta">How can you configure environment variables in AWS Lambda?</b>

    - Environment variables in AWS Lambda can be configured through the AWS Management Console, AWS CLI, or AWS SDKs. You can specify environment variables when creating or updating Lambda functions, and your code can access them at runtime.

7. <b style="color:magenta">What is the maximum execution time for an AWS Lambda function?</b>

    - The maximum execution time for an AWS Lambda function is 15 minutes.

8. <b style="color:magenta">How can you trigger an AWS Lambda function?</b>

    - AWS Lambda functions can be triggered in response to various events. Some common triggers include changes to data in an Amazon S3 bucket, updates to a DynamoDB table, or an HTTP request via Amazon API Gateway.

9. <b style="color:magenta">Explain what an AWS Lambda Layer is.</b>

    - An AWS Lambda Layer is a distribution mechanism for libraries, custom runtimes, and other function dependencies. It allows you to manage your in-use libraries separately from your function code, reducing the size of your deployment package.

10. <b style="color:magenta">What is the maximum size of a deployment package for an AWS Lambda function?</b>

    - The maximum size for an AWS Lambda function deployment package is 50 MB when zipped for direct upload, and 250 MB when unzipped. For .zip files greater than 50MB, you must upload your package to an Amazon S3 bucket first.
    - These questions cover a range of topics related to AWS Lambda, including its features, components, pricing, and usage. Be sure to tailor your answers based on your specific experiences and understanding of AWS Lambda concepts.

11. <b style="color:magenta">What is the size limit for Lambda function container?</b>
    Lambda supports a maximum uncompressed image size of 10 GB, including all layers.

</details>
