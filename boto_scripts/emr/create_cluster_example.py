#!/usr/bin/env python3
"""
Example script showing how to create EMR clusters with different configurations

This script demonstrates various EMR cluster configurations for different use cases:
1. Development cluster (small, cost-effective)
2. Production cluster (large, high-availability)
3. Spot instance cluster (cost-optimized)
4. Machine learning cluster (GPU instances)
5. Streaming cluster (optimized for real-time processing)

Author: AWS Data Engineering Team
Version: 1.0.0
"""

import os
import sys
import json
from datetime import datetime

# Add parent directory to path to import EMRClusterCreator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cluster_creator import EMRClusterCreator


def create_development_cluster():
    """Create a small development cluster"""
    config = {
        "cluster_name": "dev-emr-cluster",
        "release_label": "emr-6.15.0",
        "applications": [
            {"Name": "Spark"},
            {"Name": "Hadoop"},
            {"Name": "Hive"},
            {"Name": "Zeppelin"},
            {"Name": "JupyterHub"},
        ],
        "master_instance": {"instance_type": "m5.large", "market": "ON_DEMAND"},
        "core_instances": {
            "instance_type": "m5.large",
            "instance_count": 1,
            "market": "ON_DEMAND",
        },
        "keep_alive": True,
        "termination_protected": False,
        "visible_to_all_users": True,
        "tags": [
            {"Key": "Environment", "Value": "development"},
            {"Key": "Project", "Value": "data-exploration"},
            {"Key": "Owner", "Value": "dev-team"},
            {"Key": "CreatedBy", "Value": "EMRClusterCreator"},
            {"Key": "CreatedAt", "Value": datetime.now().isoformat()},
        ],
    }
    return config


def create_production_cluster():
    """Create a production-ready cluster with high availability"""
    config = {
        "cluster_name": "prod-emr-cluster",
        "release_label": "emr-6.15.0",
        "applications": [
            {"Name": "Spark"},
            {"Name": "Hadoop"},
            {"Name": "Hive"},
            {"Name": "Pig"},
            {"Name": "Presto"},
            {"Name": "Ganglia"},
        ],
        "configurations": [
            {
                "Classification": "spark-defaults",
                "Properties": {
                    "spark.sql.adaptive.enabled": "true",
                    "spark.sql.adaptive.coalescePartitions.enabled": "true",
                    "spark.sql.adaptive.skewJoin.enabled": "true",
                    "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
                    "spark.dynamicAllocation.enabled": "true",
                    "spark.dynamicAllocation.minExecutors": "2",
                    "spark.dynamicAllocation.maxExecutors": "20",
                    "spark.sql.execution.arrow.pyspark.enabled": "true",
                },
            },
            {
                "Classification": "yarn-site",
                "Properties": {
                    "yarn.nodemanager.vmem-check-enabled": "false",
                    "yarn.nodemanager.pmem-check-enabled": "false",
                    "yarn.scheduler.maximum-allocation-mb": "14336",
                    "yarn.scheduler.maximum-allocation-vcores": "4",
                },
            },
        ],
        "master_instance": {
            "instance_type": "m5.xlarge",
            "market": "ON_DEMAND",
            "ebs_config": {
                "EbsBlockDeviceConfigs": [
                    {
                        "VolumeSpecification": {
                            "SizeInGB": 200,
                            "VolumeType": "gp3",
                            "Iops": 3000,
                            "Throughput": 125,
                        },
                        "VolumesPerInstance": 1,
                    }
                ],
                "EbsOptimized": True,
            },
        },
        "core_instances": {
            "instance_type": "m5.2xlarge",
            "instance_count": 4,
            "market": "ON_DEMAND",
            "ebs_config": {
                "EbsBlockDeviceConfigs": [
                    {
                        "VolumeSpecification": {
                            "SizeInGB": 200,
                            "VolumeType": "gp3",
                            "Iops": 3000,
                            "Throughput": 125,
                        },
                        "VolumesPerInstance": 2,
                    }
                ],
                "EbsOptimized": True,
            },
            "auto_scaling": {
                "min_capacity": 2,
                "max_capacity": 20,
                "rules": [
                    {
                        "Name": "ScaleOutMemoryPercentage",
                        "Description": "Scale out if YARNMemoryAvailablePercentage is less than 15",
                        "Action": {
                            "Market": "ON_DEMAND",
                            "SimpleScalingPolicyConfiguration": {
                                "AdjustmentType": "CHANGE_IN_CAPACITY",
                                "ScalingAdjustment": 2,
                                "CoolDown": 300,
                            },
                        },
                        "Trigger": {
                            "CloudWatchAlarmDefinition": {
                                "ComparisonOperator": "LESS_THAN",
                                "EvaluationPeriods": 2,
                                "MetricName": "YARNMemoryAvailablePercentage",
                                "Namespace": "AWS/ElasticMapReduce",
                                "Period": 300,
                                "Statistic": "AVERAGE",
                                "Threshold": 15.0,
                                "Unit": "PERCENT",
                            }
                        },
                    }
                ],
            },
        },
        "keep_alive": True,
        "termination_protected": True,
        "visible_to_all_users": True,
        "step_concurrency_level": 2,
        "managed_scaling_policy": {
            "ComputeLimits": {
                "UnitType": "Instances",
                "MinimumCapacityUnits": 2,
                "MaximumCapacityUnits": 20,
                "MaximumOnDemandCapacityUnits": 10,
                "MaximumCoreCapacityUnits": 10,
            }
        },
        "bootstrap_actions": [
            {
                "Name": "Install Production Packages",
                "ScriptBootstrapAction": {
                    "Path": "s3://your-bucket/bootstrap-scripts/install-packages.sh",
                    "Args": [
                        "--packages",
                        "pandas,numpy,scikit-learn,boto3,psycopg2-binary",
                        "--monitoring-tools",
                    ],
                },
            }
        ],
        "tags": [
            {"Key": "Environment", "Value": "production"},
            {"Key": "Project", "Value": "data-pipeline"},
            {"Key": "Owner", "Value": "data-team"},
            {"Key": "CostCenter", "Value": "12345"},
            {"Key": "CreatedBy", "Value": "EMRClusterCreator"},
            {"Key": "CreatedAt", "Value": datetime.now().isoformat()},
        ],
    }
    return config


def create_spot_cluster():
    """Create a cost-optimized cluster using spot instances"""
    config = {
        "cluster_name": "spot-emr-cluster",
        "release_label": "emr-6.15.0",
        "applications": [{"Name": "Spark"}, {"Name": "Hadoop"}, {"Name": "Hive"}],
        "master_instance": {
            "instance_type": "m5.large",
            "market": "ON_DEMAND",  # Keep master on-demand for stability
        },
        "core_instances": {
            "instance_type": "m5.large",
            "instance_count": 2,
            "market": "SPOT",
            "bid_price": "0.08",  # Adjust based on current spot prices
        },
        "task_instances": {
            "instance_type": "m5.large",
            "instance_count": 4,
            "market": "SPOT",
            "bid_price": "0.08",
        },
        "keep_alive": True,
        "termination_protected": False,
        "scale_down_behavior": "TERMINATE_AT_TASK_COMPLETION",
        "tags": [
            {"Key": "Environment", "Value": "development"},
            {"Key": "Project", "Value": "batch-processing"},
            {"Key": "Owner", "Value": "data-team"},
            {"Key": "CostOptimized", "Value": "true"},
            {"Key": "CreatedBy", "Value": "EMRClusterCreator"},
            {"Key": "CreatedAt", "Value": datetime.now().isoformat()},
        ],
    }
    return config


def create_ml_cluster():
    """Create a machine learning cluster with GPU instances"""
    config = {
        "cluster_name": "ml-emr-cluster",
        "release_label": "emr-6.15.0",
        "applications": [
            {"Name": "Spark"},
            {"Name": "Hadoop"},
            {"Name": "JupyterHub"},
            {"Name": "Zeppelin"},
            {"Name": "TensorFlow"},
            {"Name": "MXNet"},
        ],
        "configurations": [
            {
                "Classification": "spark-defaults",
                "Properties": {
                    "spark.sql.adaptive.enabled": "true",
                    "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
                    "spark.dynamicAllocation.enabled": "true",
                    "spark.dynamicAllocation.minExecutors": "1",
                    "spark.dynamicAllocation.maxExecutors": "10",
                    "spark.rapids.sql.enabled": "true",  # Enable GPU acceleration
                    "spark.plugins": "com.nvidia.spark.SQLPlugin",
                },
            }
        ],
        "master_instance": {"instance_type": "m5.xlarge", "market": "ON_DEMAND"},
        "core_instances": {
            "instance_type": "p3.2xlarge",  # GPU instances
            "instance_count": 2,
            "market": "ON_DEMAND",
            "ebs_config": {
                "EbsBlockDeviceConfigs": [
                    {
                        "VolumeSpecification": {
                            "SizeInGB": 500,
                            "VolumeType": "gp3",
                            "Iops": 3000,
                        },
                        "VolumesPerInstance": 1,
                    }
                ],
                "EbsOptimized": True,
            },
        },
        "bootstrap_actions": [
            {
                "Name": "Install ML Packages",
                "ScriptBootstrapAction": {
                    "Path": "s3://your-bucket/bootstrap-scripts/install-packages.sh",
                    "Args": [
                        "--packages",
                        "tensorflow,torch,transformers,datasets,accelerate",
                        "--jupyter-extensions",
                    ],
                },
            }
        ],
        "keep_alive": True,
        "termination_protected": False,
        "tags": [
            {"Key": "Environment", "Value": "development"},
            {"Key": "Project", "Value": "machine-learning"},
            {"Key": "Owner", "Value": "ml-team"},
            {"Key": "GPUEnabled", "Value": "true"},
            {"Key": "CreatedBy", "Value": "EMRClusterCreator"},
            {"Key": "CreatedAt", "Value": datetime.now().isoformat()},
        ],
    }
    return config


def create_streaming_cluster():
    """Create a cluster optimized for streaming workloads"""
    config = {
        "cluster_name": "streaming-emr-cluster",
        "release_label": "emr-6.15.0",
        "applications": [
            {"Name": "Spark"},
            {"Name": "Hadoop"},
            {"Name": "Flink"},
            {"Name": "Zeppelin"},
            {"Name": "Ganglia"},
        ],
        "configurations": [
            {
                "Classification": "spark-defaults",
                "Properties": {
                    "spark.sql.adaptive.enabled": "true",
                    "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
                    "spark.streaming.backpressure.enabled": "true",
                    "spark.streaming.receiver.maxRate": "10000",
                    "spark.streaming.kafka.maxRatePerPartition": "1000",
                    "spark.sql.streaming.checkpointLocation": "/tmp/spark-checkpoints",
                },
            },
            {
                "Classification": "flink-conf",
                "Properties": {
                    "taskmanager.memory.process.size": "4096m",
                    "jobmanager.memory.process.size": "2048m",
                    "taskmanager.numberOfTaskSlots": "4",
                },
            },
        ],
        "master_instance": {"instance_type": "m5.xlarge", "market": "ON_DEMAND"},
        "core_instances": {
            "instance_type": "r5.large",  # Memory-optimized for streaming
            "instance_count": 3,
            "market": "ON_DEMAND",
            "auto_scaling": {"min_capacity": 2, "max_capacity": 10},
        },
        "task_instances": {
            "instance_type": "r5.large",
            "instance_count": 2,
            "market": "SPOT",
            "bid_price": "0.10",
        },
        "keep_alive": True,
        "termination_protected": False,
        "step_concurrency_level": 3,
        "tags": [
            {"Key": "Environment", "Value": "production"},
            {"Key": "Project", "Value": "real-time-analytics"},
            {"Key": "Owner", "Value": "streaming-team"},
            {"Key": "Workload", "Value": "streaming"},
            {"Key": "CreatedBy", "Value": "EMRClusterCreator"},
            {"Key": "CreatedAt", "Value": datetime.now().isoformat()},
        ],
    }
    return config


def main():
    """Main function to demonstrate cluster creation"""
    # Get AWS configuration
    aws_profile = os.getenv("AWS_PROFILE")
    aws_region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

    # Initialize EMR cluster creator
    emr_creator = EMRClusterCreator(aws_profile=aws_profile, region=aws_region)

    # Available cluster configurations
    cluster_configs = {
        "development": create_development_cluster(),
        "production": create_production_cluster(),
        "spot": create_spot_cluster(),
        "ml": create_ml_cluster(),
        "streaming": create_streaming_cluster(),
    }

    # Get cluster type from command line or environment
    cluster_type = (
        sys.argv[1] if len(sys.argv) > 1 else os.getenv("CLUSTER_TYPE", "development")
    )

    if cluster_type not in cluster_configs:
        print(f"Invalid cluster type: {cluster_type}")
        print(f"Available types: {', '.join(cluster_configs.keys())}")
        sys.exit(1)

    config = cluster_configs[cluster_type]

    print(f"Creating {cluster_type} EMR cluster...")
    print(f"Configuration: {json.dumps(config, indent=2, default=str)}")

    try:
        # Set up prerequisites (VPC, IAM roles, etc.)
        if not config.get("vpc_id"):
            vpcs = emr_creator.ec2_client.describe_vpcs(
                Filters=[{"Name": "is-default", "Values": ["true"]}]
            )
            if vpcs["Vpcs"]:
                config["vpc_id"] = vpcs["Vpcs"][0]["VpcId"]

        if not config.get("subnet_id") and config.get("vpc_id"):
            subnets = emr_creator.ec2_client.describe_subnets(
                Filters=[
                    {"Name": "vpc-id", "Values": [config["vpc_id"]]},
                    {"Name": "default-for-az", "Values": ["true"]},
                ]
            )
            if subnets["Subnets"]:
                config["subnet_id"] = subnets["Subnets"][0]["SubnetId"]

        # Create S3 bucket for logs
        if not config.get("log_uri"):
            bucket_name = (
                f"{config['cluster_name']}-logs-{int(datetime.now().timestamp())}"
            )
            config["log_uri"] = emr_creator.create_s3_bucket_for_logs(bucket_name)

        # Create IAM roles
        if not config.get("service_role"):
            iam_roles = emr_creator.create_iam_roles(config["cluster_name"])
            config.update(iam_roles)

        # Create security groups
        if not config.get("master_security_group"):
            security_groups = emr_creator.create_security_groups(
                config["vpc_id"], config["cluster_name"]
            )
            config.update(security_groups)

        # Create the cluster
        cluster_id = emr_creator.create_emr_cluster(config)

        print(f"\n{'=' * 60}")
        print(f"{cluster_type.upper()} EMR CLUSTER CREATED")
        print(f"{'=' * 60}")
        print(f"Cluster ID: {cluster_id}")
        print(f"Cluster Name: {config['cluster_name']}")
        print(f"Region: {aws_region}")
        print(f"Log URI: {config['log_uri']}")
        print(f"{'=' * 60}")

        # Save cluster info
        cluster_info = {
            "cluster_id": cluster_id,
            "cluster_type": cluster_type,
            "config": config,
            "created_at": datetime.now().isoformat(),
        }

        with open(f"{cluster_type}_cluster_info.json", "w") as f:
            json.dump(cluster_info, f, indent=2, default=str)

        print(f"Cluster information saved to: {cluster_type}_cluster_info.json")

    except Exception as e:
        print(f"Error creating cluster: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
