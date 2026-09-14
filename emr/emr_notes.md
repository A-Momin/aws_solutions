In the context of **AWS EMR (Elastic MapReduce)**, a **Classification** is a way to define and apply custom configurations to specific components or services running on an EMR cluster. These configurations are passed through the `Configurations` parameter when creating a cluster or modifying its settings.

#### **Purpose of Classifications**

Classifications allow you to:

1. Modify the behavior of Hadoop, Spark, Hive, HBase, and other applications.
2. Optimize resource utilization and performance.
3. Set environment-specific properties such as memory allocation, logging levels, or custom paths.

#### **Structure**

A **Classification** consists of:

-   The **Name** of the service or component to configure.
-   A list of **Properties** that are key-value pairs defining the configuration.
-   Optionally, nested **Configurations** to define sub-components or sub-configurations.

#### **Commonly Used Classifications**

Here are some common classifications and their use cases:

#### **1. `spark-defaults`**

Used to configure Apache Spark default settings:

```json
{
    "Classification": "spark-defaults",
    "Properties": {
        "spark.executor.memory": "4G",
        "spark.executor.cores": "2"
    }
}
```

-   **Example**: Set the executor memory to 4 GB and allocate 2 cores per executor.

#### **2. `hadoop-env`**

Used to modify the Hadoop environment:

```json
{
    "Classification": "hadoop-env",
    "Configurations": [
        {
            "Classification": "export",
            "Properties": {
                "JAVA_HOME": "/usr/lib/jvm/java-1.8.0"
            }
        }
    ]
}
```

-   **Example**: Set the `JAVA_HOME` path for Hadoop.

#### **3. `core-site`**

Configures HDFS core-site properties:

```json
{
    "Classification": "core-site",
    "Properties": {
        "fs.defaultFS": "hdfs://my-cluster/",
        "hadoop.tmp.dir": "/mnt/hadoop/tmp"
    }
}
```

-   **Example**: Configure the default filesystem and temporary directory.

#### **4. `mapred-site`**

Configures properties for MapReduce:

```json
{
    "Classification": "mapred-site",
    "Properties": {
        "mapreduce.framework.name": "yarn",
        "mapreduce.map.memory.mb": "2048"
    }
}
```

-   **Example**: Use YARN as the resource manager and allocate 2 GB memory for mappers.

#### **5. `emrfs-site`**

Used to configure EMRFS (EMR file system) for S3:

```json
{
    "Classification": "emrfs-site",
    "Properties": {
        "fs.s3.consistent.retryCount": "5",
        "fs.s3.consistent": "true"
    }
}
```

-   **Example**: Enable consistent view and set retry count for S3 operations.

#### **6. `yarn-site`**

Configures YARN resource manager settings:

```json
{
    "Classification": "yarn-site",
    "Properties": {
        "yarn.scheduler.maximum-allocation-mb": "8192",
        "yarn.nodemanager.resource.memory-mb": "8192"
    }
}
```

-   **Example**: Configure the maximum memory allocation for YARN applications.

#### **How to Use Classifications**

You can specify classifications when creating or updating an EMR cluster:

1. **Using the AWS Management Console**:

    - While creating a cluster, go to the "Edit software settings" section and add configurations.

2. **Using AWS CLI**:
   Example:

    ```bash
    aws emr create-cluster \
        --name "MyCluster" \
        --release-label emr-6.3.0 \
        --applications Name=Hadoop Name=Spark \
        --configurations file://configurations.json
    ```

    Example `configurations.json`:

    ```json
    [
        {
            "Classification": "spark-defaults",
            "Properties": {
                "spark.executor.memory": "4G"
            }
        },
        {
            "Classification": "hadoop-env",
            "Configurations": [
                {
                    "Classification": "export",
                    "Properties": {
                        "JAVA_HOME": "/usr/lib/jvm/java-1.8.0"
                    }
                }
            ]
        }
    ]
    ```

3. **Using Boto3**:
   Example:
    ```python
    response = emr_client.run_job_flow(
        Name="MyCluster",
        Configurations=[
            {
                "Classification": "spark-defaults",
                "Properties": {"spark.executor.memory": "4G"}
            },
            {
                "Classification": "hadoop-env",
                "Configurations": [
                    {
                        "Classification": "export",
                        "Properties": {"JAVA_HOME": "/usr/lib/jvm/java-1.8.0"}
                    }
                ]
            }
        ]
    )
    ```

#### **Additional Notes**

-   Classifications are predefined for each supported application and release version of EMR.
-   Ensure compatibility with your EMR version by consulting the [EMR Release Guide](https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-release-components.html).
-   Misconfigured classifications can result in cluster launch failures or misbehaving components.

Let me know if you need help with specific configurations!

```python
EMR_SERVICE_ROLE_NAME="EMR_DefaultRole"

# ServiceRole Trust Policy (for EMR service)
assume_role_policy_doc = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "elasticmapreduce.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}

EMR_ROLE_ARN = iam_client.create_role(
    RoleName=EMR_SERVICE_ROLE_NAME,
    AssumeRolePolicyDocument=json.dumps(assume_role_policy_doc),
    Description="EMR Service Role"
)['Role']['Arn']

# AWS Managed Policy
iam_client.attach_role_policy(RoleName=EMR_SERVICE_ROLE_NAME, PolicyArn="arn:aws:iam::aws:policy/service-role/AmazonEMRServicePolicy_v2")

# Custom Managed Policy
amazon_emr_service_role_policy={
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "CreateInNetwork",
            "Effect": "Allow",
            "Action": [
                "ec2:CreateNetworkInterface",
                "ec2:RunInstances",
                "ec2:CreateFleet",
                "ec2:CreateLaunchTemplate",
                "ec2:CreateLaunchTemplateVersion"
            ],
            "Resource": [
                "arn:aws:ec2:*:*:subnet/subnet-0980ad10eb313405b",
                "arn:aws:ec2:*:*:security-group/sg-013cd214cf27146c6",
                "arn:aws:ec2:*:*:security-group/sg-05199d215981f1520"
            ]
        },
        {
            "Sid": "ManageSecurityGroups",
            "Effect": "Allow",
            "Action": [
                "ec2:AuthorizeSecurityGroupEgress",
                "ec2:AuthorizeSecurityGroupIngress",
                "ec2:RevokeSecurityGroupEgress",
                "ec2:RevokeSecurityGroupIngress"
            ],
            "Resource": [
                "arn:aws:ec2:*:*:security-group/sg-013cd214cf27146c6",
                "arn:aws:ec2:*:*:security-group/sg-05199d215981f1520"
            ]
        },
        {
            "Sid": "CreateDefaultSecurityGroupInVPC",
            "Effect": "Allow",
            "Action": [
                "ec2:CreateSecurityGroup"
            ],
            "Resource": [
                "arn:aws:ec2:*:*:vpc/vpc-03617a8a518caa526"
            ]
        },
        {
            "Sid": "PassRoleForEC2",
            "Effect": "Allow",
            "Action": "iam:PassRole",
            "Resource": "arn:aws:iam::381492255899:role/service-role/AmazonEMR-InstanceProfile-20241205T130626",
            "Condition": {
                "StringLike": {
                    "iam:PassedToService": "ec2.amazonaws.com"
                }
            }
        }
    ]
}

# Attach the inline policy to the IAM role
iam_client.put_role_policy(
    RoleName=EMR_SERVICE_ROLE_NAME,
    PolicyName="EMR_put_event",
    PolicyDocument=json.dumps(amazon_emr_service_role_policy)
)

EMR_PROFILE_NAME = "emr_instance_profile"  # Name for the instance profile
EMR_JOB_FLOW_ROLE_ROLE_NAME = "EMR_EC2_DefaultRole"

job_flow_role_trust_policy_doc = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}

JOB_FLOW_ROLE_ARN = iam_client.create_role(
    RoleName=EMR_JOB_FLOW_ROLE_ROLE_NAME,
    AssumeRolePolicyDocument=json.dumps(job_flow_role_trust_policy_doc),
    Description="EMR Service Role"
)['Role']['Arn']

amazon_emr_instance_profile_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:AbortMultipartUpload",
                "s3:CreateBucket",
                "s3:DeleteObject",
                "s3:GetBucketVersioning",
                "s3:GetObject",
                "s3:GetObjectTagging",
                "s3:GetObjectVersion",
                "s3:ListBucket",
                "s3:ListBucketMultipartUploads",
                "s3:ListBucketVersions",
                "s3:ListMultipartUploadParts",
                "s3:PutBucketVersioning",
                "s3:PutObject",
                "s3:PutObjectTagging"
            ],
            "Resource": [
                "arn:aws:s3:::*"
            ]
        }
    ]
}


# Attach the inline policy to the IAM role
iam_client.put_role_policy(
    RoleName=EMR_JOB_FLOW_ROLE_ROLE_NAME,
    PolicyName="EMR_put_event",
    PolicyDocument=json.dumps(amazon_emr_instance_profile_policy)
)

# Create the instance profile
print(f"Creating instance profile: {EMR_PROFILE_NAME}")
iam_client.create_instance_profile(InstanceProfileName=EMR_PROFILE_NAME)

# Attach the role to the instance profile
print(f"Attaching role '{EMR_JOB_FLOW_ROLE_ROLE_NAME}' to instance profile '{EMR_PROFILE_NAME}'")
iam_client.add_role_to_instance_profile(
    InstanceProfileName=EMR_PROFILE_NAME,
    RoleName=EMR_JOB_FLOW_ROLE_ROLE_NAME
)

CLUSTER_NAME=f"emr-cluster2-{date.today().strftime('%Y%m%d')}"

response = emr_client.run_job_flow(
    Name="MyEMRCluster",
    LogUri=f"s3://{EMR_BUCKET_NAME}/{logs}/",
    ReleaseLabel="emr-5.32.0",
    Instances={
        "InstanceGroups": [
            {
                "InstanceRole": "MASTER",
                "InstanceType": "m5.xlarge",
                "InstanceCount": 1,
                "Market": "ON_DEMAND"
            },
            {
                "InstanceRole": "CORE",
                "InstanceType": "m5.xlarge",
                "InstanceCount": 2,
                "Market": "ON_DEMAND"
            }
        ],
        "Ec2KeyName": "AMominNJ",
        "KeepJobFlowAliveWhenNoSteps": True,
        "TerminationProtected": False,
        "Ec2SubnetId": SUBNET_ID,
    },
    JobFlowRole=EMR_JOB_FLOW_ROLE_ROLE_NAME,  # Ensure this role is correct
    ServiceRole=EMR_SERVICE_ROLE_NAME,
    InstanceProfile=instance_profile_arn  # Use the correct instance profile ARN
)
```
