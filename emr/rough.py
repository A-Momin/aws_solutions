import boto3, botocore
from botocore.exceptions import ClientError
import os, time, json, io, zipfile
from datetime import date
import datetime
from dateutil.tz import tzlocal
from misc import load_from_yaml, save_to_yaml
import iam, s3, lf, rds, networking, ec2

ACCOUNT_ID       = os.environ['AWS_ACCOUNT_ID_ROOT']
REGION           = os.environ['AWS_DEFAULT_REGION']

iam_client           = boto3.client('iam')
ec2_client           = boto3.client('ec2', region_name=REGION)

EMR_SERVICE_ROLE_NAME="EMR_DefaultRole"

# ServiceRole Trust Policy (for EMR service)
assume_role_policy_doc = {
    "Version": "2008-10-17",
    "Statement": [
        {
            "Sid": "",
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
iam_client.attach_role_policy(RoleName=EMR_SERVICE_ROLE_NAME, PolicyArn="arn:aws:iam::aws:policy/service-role/AmazonElasticMapReduceRole")

EMR_AUTOSCALING_DEFAULT_ROLE="EMR_AutoScaling_DefaultRole"

# ServiceRole Trust Policy (for EMR service)
emr_autoscaling_defaultrole_trust_relationships = {
    "Version": "2008-10-17",
    "Statement": [
        {
            "Sid": "",
            "Effect": "Allow",
            "Principal": {
                "Service": [
                    "elasticmapreduce.amazonaws.com",
                    "application-autoscaling.amazonaws.com"
                ]
            },
            "Action": "sts:AssumeRole"
        }
    ]
}

EMR_AUTOSCALING_DEFAULT_ROLE_ARN = iam_client.create_role(
    RoleName=EMR_AUTOSCALING_DEFAULT_ROLE,
    AssumeRolePolicyDocument=json.dumps(emr_autoscaling_defaultrole_trust_relationships),
    Description="EMR Service Role"
)['Role']['Arn']

# AWS Managed Policy
iam_client.attach_role_policy(RoleName=EMR_SERVICE_ROLE_NAME, PolicyArn="arn:aws:iam::aws:policy/service-role/AmazonElasticMapReduceforAutoScalingRole")

EMR_PROFILE_NAME = "emr_instance_profile"  # Name for the instance profile
EMR_JOB_FLOW_ROLE_ROLE_NAME = "EMR_EC2_DefaultRole"

job_flow_role_trust_policy_doc = {
	"Version": "2008-10-17",
	"Statement": [
		{
			"Sid": "",
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

iam_client.attach_role_policy(RoleName=EMR_JOB_FLOW_ROLE_ROLE_NAME, PolicyArn="arn:aws:iam::aws:policy/service-role/AmazonElasticMapReduceforEC2Role")

# # Create the instance profile
# print(f"Creating instance profile: {EMR_PROFILE_NAME}")
# iam_client.create_instance_profile(InstanceProfileName=EMR_PROFILE_NAME)

# Attach the role to the instance profile
print(f"Attaching role '{EMR_JOB_FLOW_ROLE_ROLE_NAME}' to instance profile '{EMR_PROFILE_NAME}'")
iam_client.add_role_to_instance_profile(
    InstanceProfileName=EMR_PROFILE_NAME,
    RoleName=EMR_JOB_FLOW_ROLE_ROLE_NAME
)

ec2_client.associate_iam_instance_profile(
    IamInstanceProfile={'Name': EMR_PROFILE_NAME},
    InstanceId=""
)