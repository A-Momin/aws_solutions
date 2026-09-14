#!/usr/bin/env python3
"""
EMR Configuration Builder

Interactive script to build EMR cluster configuration with all possible options.
This helps users create customized configurations without manually editing the main script.

Author: AWS Data Engineering Team
Version: 1.0.0
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import argparse


class EMRConfigBuilder:
    """Interactive EMR configuration builder"""

    def __init__(self):
        self.config = {}
        self.instance_types = [
            "m5.large",
            "m5.xlarge",
            "m5.2xlarge",
            "m5.4xlarge",
            "m5.8xlarge",
            "m5.12xlarge",
            "m5.16xlarge",
            "m5.24xlarge",
            "m5d.large",
            "m5d.xlarge",
            "m5d.2xlarge",
            "m5d.4xlarge",
            "m5d.8xlarge",
            "m5d.12xlarge",
            "m5d.16xlarge",
            "m5d.24xlarge",
            "m5a.large",
            "m5a.xlarge",
            "m5a.2xlarge",
            "m5a.4xlarge",
            "m5a.8xlarge",
            "m5a.12xlarge",
            "m5a.16xlarge",
            "m5a.24xlarge",
            "c5.large",
            "c5.xlarge",
            "c5.2xlarge",
            "c5.4xlarge",
            "c5.9xlarge",
            "c5.12xlarge",
            "c5.18xlarge",
            "c5.24xlarge",
            "c5d.large",
            "c5d.xlarge",
            "c5d.2xlarge",
            "c5d.4xlarge",
            "c5d.9xlarge",
            "c5d.12xlarge",
            "c5d.18xlarge",
            "c5d.24xlarge",
            "r5.large",
            "r5.xlarge",
            "r5.2xlarge",
            "r5.4xlarge",
            "r5.8xlarge",
            "r5.12xlarge",
            "r5.16xlarge",
            "r5.24xlarge",
            "r5d.large",
            "r5d.xlarge",
            "r5d.2xlarge",
            "r5d.4xlarge",
            "r5d.8xlarge",
            "r5d.12xlarge",
            "r5d.16xlarge",
            "r5d.24xlarge",
            "i3.large",
            "i3.xlarge",
            "i3.2xlarge",
            "i3.4xlarge",
            "i3.8xlarge",
            "i3.16xlarge",
            "i3en.large",
            "i3en.xlarge",
            "i3en.2xlarge",
            "i3en.3xlarge",
            "i3en.6xlarge",
            "i3en.12xlarge",
            "i3en.24xlarge",
        ]

        self.emr_releases = [
            "emr-6.15.0",
            "emr-6.14.0",
            "emr-6.13.0",
            "emr-6.12.0",
            "emr-6.11.0",
            "emr-6.10.0",
            "emr-6.9.0",
            "emr-6.8.0",
            "emr-6.7.0",
            "emr-6.6.0",
            "emr-5.36.0",
            "emr-5.35.0",
            "emr-5.34.0",
            "emr-5.33.0",
            "emr-5.32.0",
        ]

        self.applications = [
            "Spark",
            "Hadoop",
            "Hive",
            "Pig",
            "HBase",
            "Presto",
            "Zeppelin",
            "JupyterHub",
            "Livy",
            "Ganglia",
            "Sqoop",
            "Oozie",
            "Phoenix",
            "Flink",
            "MXNet",
            "TensorFlow",
            "Mahout",
            "Hue",
        ]

    def get_input(self,prompt: str,default: Any = None,input_type: type = str,choices: List[str] = None,) -> Any:
        """Get user input with validation"""
        while True:
            if default is not None:
                user_input = input(f"{prompt} [{default}]: ").strip()
                if not user_input:
                    return default
            else:
                user_input = input(f"{prompt}: ").strip()
                if not user_input:
                    print("This field is required. Please enter a value.")
                    continue

            if choices and user_input not in choices:
                print(f"Invalid choice. Please select from: {', '.join(choices)}")
                continue

            try:
                if input_type == bool:
                    return user_input.lower() in ["true", "yes", "y", "1"]
                elif input_type == int:
                    return int(user_input)
                elif input_type == float:
                    return float(user_input)
                else:
                    return user_input
            except ValueError:
                print(f"Invalid input. Please enter a valid {input_type.__name__}.")
                continue

    def select_multiple(self, prompt: str, choices: List[str], default: List[str] = None) -> List[str]:
        """Select multiple items from a list"""
        print(f"\n{prompt}")
        print("Available options:")
        for i, choice in enumerate(choices, 1):
            print(f"  {i}. {choice}")

        if default:
            print(f"Default: {', '.join(default)}")

        while True:
            user_input = input(
                "Enter numbers separated by commas (e.g., 1,3,5) or press Enter for default: "
            ).strip()

            if not user_input and default:
                return default

            if not user_input:
                print("Please make a selection or press Enter for default.")
                continue

            try:
                indices = [int(x.strip()) - 1 for x in user_input.split(",")]
                selected = [choices[i] for i in indices if 0 <= i < len(choices)]

                if not selected:
                    print("No valid selections made. Please try again.")
                    continue

                return selected
            except (ValueError, IndexError):
                print("Invalid input. Please enter valid numbers separated by commas.")
                continue

    def build_basic_config(self):
        """Build basic cluster configuration"""
        print("\n" + "=" * 60)
        print("BASIC CLUSTER CONFIGURATION")
        print("=" * 60)

        self.config["cluster_name"] = self.get_input("Cluster name", "my-emr-cluster")

        print("\nEMR Release Label:")
        for i, release in enumerate(self.emr_releases[:10], 1):
            print(f"  {i}. {release}")

        release_choice = self.get_input("Select EMR release (1-10)", 1, int)
        self.config["release_label"] = self.emr_releases[release_choice - 1]

        # Applications
        default_apps = ["Spark", "Hadoop", "Hive", "Zeppelin", "JupyterHub"]
        selected_apps = self.select_multiple(
            "Select applications to install:", self.applications, default_apps
        )
        self.config["applications"] = [{"Name": app} for app in selected_apps]

    def build_instance_config(self):
        """Build instance configuration"""
        print("\n" + "=" * 60)
        print("INSTANCE CONFIGURATION")
        print("=" * 60)

        # Master instance
        print("\n--- Master Instance ---")
        master_type = self.get_input(
            "Master instance type", "m5.xlarge", choices=self.instance_types
        )
        master_market = self.get_input(
            "Master market type", "ON_DEMAND", choices=["ON_DEMAND", "SPOT"]
        )

        master_config = {"instance_type": master_type, "market": master_market}

        if master_market == "SPOT":
            master_config["bid_price"] = str(
                self.get_input("Master spot bid price", 0.10, float)
            )

        # EBS configuration for master
        use_ebs = self.get_input("Configure EBS for master", True, bool)
        if use_ebs:
            ebs_size = self.get_input("EBS volume size (GB)", 100, int)
            ebs_type = self.get_input(
                "EBS volume type", "gp3", choices=["gp2", "gp3", "io1", "io2"]
            )

            master_config["ebs_config"] = {
                "EbsBlockDeviceConfigs": [
                    {
                        "VolumeSpecification": {
                            "SizeInGB": ebs_size,
                            "VolumeType": ebs_type,
                        },
                        "VolumesPerInstance": 1,
                    }
                ],
                "EbsOptimized": True,
            }

        self.config["master_instance"] = master_config

        # Core instances
        print("\n--- Core Instances ---")
        core_count = self.get_input("Number of core instances", 2, int)

        if core_count > 0:
            core_type = self.get_input(
                "Core instance type", "m5.large", choices=self.instance_types
            )
            core_market = self.get_input(
                "Core market type", "ON_DEMAND", choices=["ON_DEMAND", "SPOT"]
            )

            core_config = {
                "instance_type": core_type,
                "instance_count": core_count,
                "market": core_market,
            }

            if core_market == "SPOT":
                core_config["bid_price"] = str(
                    self.get_input("Core spot bid price", 0.05, float)
                )

            # EBS configuration for core
            use_ebs = self.get_input("Configure EBS for core instances", True, bool)
            if use_ebs:
                ebs_size = self.get_input("EBS volume size (GB)", 100, int)
                ebs_type = self.get_input(
                    "EBS volume type", "gp3", choices=["gp2", "gp3", "io1", "io2"]
                )
                volumes_per_instance = self.get_input("Volumes per instance", 2, int)

                core_config["ebs_config"] = {
                    "EbsBlockDeviceConfigs": [
                        {
                            "VolumeSpecification": {
                                "SizeInGB": ebs_size,
                                "VolumeType": ebs_type,
                            },
                            "VolumesPerInstance": volumes_per_instance,
                        }
                    ],
                    "EbsOptimized": True,
                }

            # Auto scaling
            use_autoscaling = self.get_input(
                "Enable auto scaling for core instances", False, bool
            )
            if use_autoscaling:
                min_capacity = self.get_input("Minimum capacity", 1, int)
                max_capacity = self.get_input("Maximum capacity", 10, int)

                core_config["auto_scaling"] = {
                    "min_capacity": min_capacity,
                    "max_capacity": max_capacity,
                }

            self.config["core_instances"] = core_config

        # Task instances
        print("\n--- Task Instances (Optional) ---")
        task_count = self.get_input("Number of task instances", 0, int)

        if task_count > 0:
            task_type = self.get_input(
                "Task instance type", "m5.large", choices=self.instance_types
            )
            task_market = self.get_input(
                "Task market type", "SPOT", choices=["ON_DEMAND", "SPOT"]
            )

            task_config = {
                "instance_type": task_type,
                "instance_count": task_count,
                "market": task_market,
            }

            if task_market == "SPOT":
                task_config["bid_price"] = str(
                    self.get_input("Task spot bid price", 0.05, float)
                )

            self.config["task_instances"] = task_config

    def build_network_config(self):
        """Build network configuration"""
        print("\n" + "=" * 60)
        print("NETWORK CONFIGURATION")
        print("=" * 60)

        self.config["vpc_id"] = self.get_input("VPC ID (leave empty for default)", None)
        self.config["subnet_id"] = self.get_input(
            "Subnet ID (leave empty for default)", None
        )
        self.config["ec2_key_name"] = self.get_input(
            "EC2 Key Pair name (for SSH access)", None
        )

    def build_security_config(self):
        """Build security configuration"""
        print("\n" + "=" * 60)
        print("SECURITY CONFIGURATION")
        print("=" * 60)

        # Security groups
        self.config["master_security_group"] = self.get_input(
            "Master security group ID (leave empty to create)", None
        )
        self.config["worker_security_group"] = self.get_input(
            "Worker security group ID (leave empty to create)", None
        )
        self.config["service_security_group"] = self.get_input(
            "Service security group ID (leave empty to create)", None
        )

        # IAM roles
        self.config["service_role"] = self.get_input(
            "EMR service role ARN (leave empty to create)", None
        )
        self.config["instance_profile"] = self.get_input(
            "EC2 instance profile name (leave empty to create)", None
        )
        self.config["autoscaling_role"] = self.get_input(
            "Auto scaling role ARN (leave empty to create)", None
        )

    def build_logging_config(self):
        """Build logging configuration"""
        print("\n" + "=" * 60)
        print("LOGGING CONFIGURATION")
        print("=" * 60)

        self.config["log_uri"] = self.get_input(
            "S3 log URI (leave empty to create bucket)", None
        )
        if not self.config["log_uri"]:
            self.config["log_bucket_name"] = self.get_input(
                "S3 log bucket name (leave empty for auto-generated)", None
            )

    def build_advanced_config(self):
        """Build advanced configuration"""
        print("\n" + "=" * 60)
        print("ADVANCED CONFIGURATION")
        print("=" * 60)

        self.config["keep_alive"] = self.get_input(
            "Keep cluster alive when no steps", True, bool
        )
        self.config["termination_protected"] = self.get_input(
            "Enable termination protection", False, bool
        )
        self.config["visible_to_all_users"] = self.get_input(
            "Visible to all IAM users", True, bool
        )

        # Managed scaling
        use_managed_scaling = self.get_input("Enable managed scaling", False, bool)
        if use_managed_scaling:
            min_capacity = self.get_input("Minimum capacity units", 1, int)
            max_capacity = self.get_input("Maximum capacity units", 10, int)
            max_ondemand = self.get_input("Maximum on-demand capacity units", 5, int)
            max_core = self.get_input("Maximum core capacity units", 5, int)

            self.config["managed_scaling_policy"] = {
                "ComputeLimits": {
                    "UnitType": "Instances",
                    "MinimumCapacityUnits": min_capacity,
                    "MaximumCapacityUnits": max_capacity,
                    "MaximumOnDemandCapacityUnits": max_ondemand,
                    "MaximumCoreCapacityUnits": max_core,
                }
            }

        # Auto termination
        use_auto_termination = self.get_input("Enable auto termination", False, bool)
        if use_auto_termination:
            idle_timeout = self.get_input("Idle timeout (seconds)", 3600, int)
            self.config["auto_termination_policy"] = {"IdleTimeout": idle_timeout}

        # Step concurrency
        self.config["step_concurrency_level"] = self.get_input(
            "Step concurrency level", 1, int
        )

        # EBS root volume size
        self.config["ebs_root_volume_size"] = self.get_input(
            "EBS root volume size (GB)", 20, int
        )

        # Repository upgrade
        repo_upgrade = self.get_input(
            "Repository upgrade on boot",
            "SECURITY",
            choices=["SECURITY", "NONE", "ALL"],
        )
        self.config["repo_upgrade_on_boot"] = repo_upgrade

    def build_spark_config(self):
        """Build Spark-specific configuration"""
        print("\n" + "=" * 60)
        print("SPARK CONFIGURATION")
        print("=" * 60)

        configure_spark = self.get_input("Configure Spark settings", True, bool)
        if not configure_spark:
            return

        spark_config = {"Classification": "spark-defaults", "Properties": {}}

        # Adaptive Query Execution
        if self.get_input("Enable Adaptive Query Execution", True, bool):
            spark_config["Properties"]["spark.sql.adaptive.enabled"] = "true"
            spark_config["Properties"][
                "spark.sql.adaptive.coalescePartitions.enabled"
            ] = "true"
            spark_config["Properties"]["spark.sql.adaptive.skewJoin.enabled"] = "true"

        # Dynamic allocation
        if self.get_input("Enable dynamic allocation", True, bool):
            spark_config["Properties"]["spark.dynamicAllocation.enabled"] = "true"
            min_executors = self.get_input("Minimum executors", 1, int)
            max_executors = self.get_input("Maximum executors", 10, int)
            spark_config["Properties"]["spark.dynamicAllocation.minExecutors"] = str(
                min_executors
            )
            spark_config["Properties"]["spark.dynamicAllocation.maxExecutors"] = str(
                max_executors
            )

        # Serializer
        if self.get_input("Use Kryo serializer", True, bool):
            spark_config["Properties"]["spark.serializer"] = (
                "org.apache.spark.serializer.KryoSerializer"
            )

        # Memory settings
        configure_memory = self.get_input("Configure memory settings", False, bool)
        if configure_memory:
            driver_memory = self.get_input("Driver memory (e.g., 4g)", "4g")
            executor_memory = self.get_input("Executor memory (e.g., 4g)", "4g")
            spark_config["Properties"]["spark.driver.memory"] = driver_memory
            spark_config["Properties"]["spark.executor.memory"] = executor_memory

        # Add to configurations
        if "configurations" not in self.config:
            self.config["configurations"] = []

        self.config["configurations"].append(spark_config)

        # Spark environment
        spark_env = {
            "Classification": "spark-env",
            "Configurations": [
                {
                    "Classification": "export",
                    "Properties": {
                        "PYSPARK_PYTHON": "/usr/bin/python3",
                        "PYSPARK_DRIVER_PYTHON": "/usr/bin/python3",
                    },
                }
            ],
        }

        self.config["configurations"].append(spark_env)

    def build_tags(self):
        """Build tags configuration"""
        print("\n" + "=" * 60)
        print("TAGS CONFIGURATION")
        print("=" * 60)

        tags = [
            {"Key": "CreatedBy", "Value": "EMRClusterCreator"},
            {"Key": "CreatedAt", "Value": datetime.now().isoformat()},
        ]

        # Environment
        environment = self.get_input(
            "Environment",
            "production",
            choices=["development", "staging", "production"],
        )
        tags.append({"Key": "Environment", "Value": environment})

        # Project
        project = self.get_input("Project name", "data-analytics")
        tags.append({"Key": "Project", "Value": project})

        # Owner
        owner = self.get_input("Owner/Team", "data-team")
        tags.append({"Key": "Owner", "Value": owner})

        # Cost center
        cost_center = self.get_input("Cost center (optional)", None)
        if cost_center:
            tags.append({"Key": "CostCenter", "Value": cost_center})

        # Additional tags
        add_more = self.get_input("Add more tags", False, bool)
        while add_more:
            key = self.get_input("Tag key")
            value = self.get_input("Tag value")
            tags.append({"Key": key, "Value": value})
            add_more = self.get_input("Add another tag", False, bool)

        self.config["tags"] = tags

    def build_configuration(self) -> Dict[str, Any]:
        """Build complete configuration interactively"""
        print("Welcome to EMR Cluster Configuration Builder!")
        print(
            "This tool will help you create a comprehensive EMR cluster configuration."
        )
        print("Press Ctrl+C at any time to exit.\n")

        try:
            self.build_basic_config()
            self.build_instance_config()
            self.build_network_config()
            self.build_security_config()
            self.build_logging_config()
            self.build_spark_config()
            self.build_advanced_config()
            self.build_tags()

            return self.config

        except KeyboardInterrupt:
            print("\n\nConfiguration building cancelled.")
            sys.exit(0)

    def save_configuration(self, config: Dict[str, Any], filename: str):
        """Save configuration to JSON file"""
        with open(filename, "w") as f:
            json.dump(config, f, indent=2, default=str)
        print(f"\nConfiguration saved to: {filename}")

    def load_configuration(self, filename: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        with open(filename, "r") as f:
            return json.load(f)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="EMR Cluster Configuration Builder")
    parser.add_argument("--load", help="Load configuration from JSON file")
    parser.add_argument("--save", help="Save configuration to JSON file", default="emr_config.json")
    parser.add_argument("--interactive", action="store_true", help="Interactive configuration builder")

    args = parser.parse_args()

    builder = EMRConfigBuilder()

    if args.load:
        try:
            config = builder.load_configuration(args.load)
            print(f"Configuration loaded from: {args.load}")
        except FileNotFoundError:
            print(f"Configuration file not found: {args.load}")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Invalid JSON in configuration file: {args.load}")
            sys.exit(1)
    else:
        config = builder.build_configuration()

    # Display configuration summary
    print("\n" + "=" * 60)
    print("CONFIGURATION SUMMARY")
    print("=" * 60)
    print(f"Cluster Name: {config.get('cluster_name', 'N/A')}")
    print(f"EMR Release: {config.get('release_label', 'N/A')}")
    print(
        f"Applications: {', '.join([app['Name'] for app in config.get('applications', [])])}"
    )
    print(
        f"Master Instance: {config.get('master_instance', {}).get('instance_type', 'N/A')}"
    )
    print(
        f"Core Instances: {config.get('core_instances', {}).get('instance_count', 0)} x {config.get('core_instances', {}).get('instance_type', 'N/A')}"
    )
    print(
        f"Task Instances: {config.get('task_instances', {}).get('instance_count', 0)} x {config.get('task_instances', {}).get('instance_type', 'N/A')}"
    )
    print(f"Keep Alive: {config.get('keep_alive', 'N/A')}")
    print(f"Termination Protected: {config.get('termination_protected', 'N/A')}")

    # Save configuration
    builder.save_configuration(config, args.save)

    print(f"\nTo create the cluster, run:")
    print(f"python emr_cluster_creator.py --config {args.save}")


if __name__ == "__main__":
    main()
