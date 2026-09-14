
### 05. [AWS CLI - Create EMR Cluster](https://learn.udacity.com/courses/ud2002/lessons/42b88ad2-df6a-47f4-95b0-9149652dea36/concepts/6d2e2f49-20fb-4599-8c48-d2dab74a0860?_gl=1*ew2n2a*_ga*OTg0ODM2NzI3LjE2OTMzMzYxOTM.*_ga_CF22GKVCFK*MTY5NDk4MjA5NC43LjEuMTY5NDk4MzI2MS42MC4wLjA.)


aws emr create-cluster --name spark-cluster \
    --use-default-roles --release-label emr-5.28.0  \
    --instance-count 3 --applications Name=Spark Name=Zeppelin  \
    --bootstrap-actions Path="s3://bootstrap.sh" \
    --ec2-attributes KeyName=AMominNJ, SubnetId=subnet-037bfc84435d21871 \
    --instance-type m5.xlarge --log-uri s3:///emrlogs/

#   `--name`: You can give any name of your choice. This will show up on your AWS EMR UI.
#   `--release-label`: This is the version of EMR you’d like to use.
#   `--instance-count`: Annotates instance count. One is for the primary, and the rest are for the secondary. For example, if `--instance-count` is given 4, then 1 instance will be reserved for primary, then 3 will be reserved for secondary instances.
#   `--applications`: List of applications you want to pre-install on your EMR at the launch time
#   `--bootstrap-actions`: The Path attribute provides the path to a file (residing in S3 or locally) that contains a script that runs during a bootstrap action. The script may set environmental variables in all the instances of the cluster. This file must be accessible to each instance in the cluster.
#   `--ec2-attributes`: The KeyName field specifies your key-pair file name, for example, if it is MyKey.pem, just specify MyKey for this field. There is one more field that you should specify, SubnetId.
#   -   The aws documentation says that the cluster must be launched within an EC2-VPC. Therefore, you need to provide the VPC subnet Id in which to create the cluster. If you do not specify this value, the cluster is launched in the normal AWS cloud, outside of any VPC. Go to the VPC service in the web console to copy any of the subnet IDs within the default VPC. If you do not see a default VPC in your account, use a simple command to create a default VPC:
#       -   `$ aws ec2 create-default-vpc --profile <profile-name>`
