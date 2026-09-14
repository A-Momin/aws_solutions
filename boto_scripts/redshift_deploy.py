#!/usr/bin/env python3
"""
Example usage of the Redshift Cluster Manager
This script demonstrates various ways to create Redshift clusters with different configurations
"""

import os
from redshift_manager import (
    RedshiftClusterManager,
    RedshiftClusterConfig,
    NetworkConfig,
    SecurityConfig,
)

from mylogger import CustomLogger
logger = CustomLogger()


#==============================================================================
RS_CLUSTER_IDENTIFIER="dev-rs-cluster"
RS_MASTER_USERNAME=os.environ["USERNAME"]
RS_MASTER_PASSWORD=os.environ["PASSWORD"]
RS_DATABASE_NAME="dev-rs-db"
#==============================================================================

def create_development_cluster():
    """Create a small development cluster"""

    cluster_config = RedshiftClusterConfig(
        cluster_identifier="dev-rs-cluster",
        master_username=os.environ["USERNAME"],
        master_password=os.environ["PASSWORD"],
        node_type="ra3.xlplus",  # dc2.large"
        cluster_type="single-node",  # Single node for dev
        database_name="dev-rs-db",
        publicly_accessible=False,
        encrypted=True,
        automated_snapshot_retention_period=1,  # Shorter retention for dev
        tags={
            "Environment": "development",
            "Team": "HTech",
            "CostCenter": "DE",
        },
    )

    # More restrictive network for dev
    network_config = NetworkConfig(
        vpc_cidr="10.1.0.0/16", subnet_cidrs=["10.1.1.0/24", "10.1.2.0/24"]
    )

    # Restrictive security - only VPC access
    security_config = SecurityConfig(allowed_cidr_blocks=["10.1.0.0/16"], port=5439)

    manager = RedshiftClusterManager()

    try:
        result = manager.create_complete_redshift_environment(
            cluster_config=cluster_config,
            network_config=network_config,
            security_config=security_config,
            resource_prefix="dev-rs",
            create_iam_role=True,
            wait_for_available=True,
        )

        logger.info("Development cluster created successfully!")
        return result

    except Exception as e:
        logger.error(f"Failed to create development cluster: {e}")
        raise


def create_production_cluster():
    """Create a production-ready cluster with all features"""

    cluster_config = RedshiftClusterConfig(
        cluster_identifier="prod-redshift-cluster",
        master_username="prodadmin",
        master_password="ProductionPassword123!",
        node_type="ra3.xlplus",  # More powerful nodes for production
        cluster_type="multi-node",
        number_of_nodes=3,
        database_name="proddb",
        publicly_accessible=False,
        encrypted=True,
        enhanced_vpc_routing=True,  # Enhanced security
        automated_snapshot_retention_period=30,  # Longer retention
        preferred_maintenance_window="sun:05:00-sun:06:00",
        enable_logging=True,
        # bucket_name="my-redshift-logs-bucket",  # Uncomment if you have S3 bucket
        tags={
            "Environment": "production",
            "Team": "data-engineering",
            "CostCenter": "analytics",
            "Backup": "required",
            "Monitoring": "enabled",
        },
    )

    network_config = NetworkConfig(
        vpc_cidr="10.0.0.0/16",
        subnet_cidrs=["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"],
    )

    security_config = SecurityConfig(
        allowed_cidr_blocks=["10.0.0.0/8"],  # Corporate network
        port=5439,
    )

    manager = RedshiftClusterManager()

    try:
        result = manager.create_complete_redshift_environment(
            cluster_config=cluster_config,
            network_config=network_config,
            security_config=security_config,
            resource_prefix="prod-rs",
            create_iam_role=True,
            create_parameter_group=True,
            parameter_group_parameters={
                "enable_user_activity_logging": "true",
                "max_concurrency_scaling_clusters": "10",
                "wlm_json_configuration": '[{"query_group":"admin","query_group_wild_card":0,"user_group":"admin","user_group_wild_card":0,"concurrency_scaling":"off","rules":[{"rule_name":"AdminRule","predicate":[{"metric_name":"query_execution_time","operator":">","value":86400}],"action":"log"}],"auto_wlm":false,"memory_percent_to_use":25,"max_execution_time":0,"queue_type":"Manual WLM","concurrency_level":5}]',
            },
            wait_for_available=True,
        )

        logger.info("Production cluster created successfully!")
        return result

    except Exception as e:
        logger.error(f"Failed to create production cluster: {e}")
        raise


def create_minimal_cluster():
    """Create a minimal cluster with basic configuration"""

    # Most basic configuration
    cluster_config = RedshiftClusterConfig(
        cluster_identifier="minimal-cluster",
        master_username="admin",
        master_password="MinimalPassword123!",
        node_type="dc2.large",
        cluster_type="single-node",
    )

    manager = RedshiftClusterManager()

    try:
        # Use all defaults for network and security
        result = manager.create_complete_redshift_environment(
            cluster_config=cluster_config,
            resource_prefix="minimal",
            create_iam_role=False,  # Skip IAM role for minimal setup
            wait_for_available=False,  # Don't wait, just start creation
        )

        logger.info("Minimal cluster creation initiated!")
        return result

    except Exception as e:
        logger.error(f"Failed to create minimal cluster: {e}")
        raise


def main():
    """Main function to demonstrate different cluster configurations"""

    print("Redshift Cluster Manager - Example Usage")
    print("=" * 50)

    # Choose which example to run
    print("\nAvailable examples:")
    print("1. Development Cluster (single-node, basic setup)")
    print("2. Production Cluster (multi-node, full features)")
    print("3. Minimal Cluster (bare minimum configuration)")
    print("4. All examples (warning: this will create multiple clusters!)")

    choice = input("\nEnter your choice (1-4): ").strip()

    try:
        if choice == "1":
            result = create_development_cluster()
            print(
                f"\nDevelopment cluster endpoint: {result['cluster_info']['Endpoint']['Address']}"
            )

        elif choice == "2":
            result = create_production_cluster()
            print(
                f"\nProduction cluster endpoint: {result['cluster_info']['Endpoint']['Address']}"
            )

        elif choice == "3":
            result = create_minimal_cluster()
            print(
                f"\nMinimal cluster creation initiated: {result['cluster_info']['ClusterIdentifier']}"
            )

        elif choice == "4":
            print("\nCreating all example clusters...")

            print("\n1. Creating development cluster...")
            dev_result = create_development_cluster()

            print("\n2. Creating production cluster...")
            prod_result = create_production_cluster()

            print("\n3. Creating minimal cluster...")
            min_result = create_minimal_cluster()

            print("\nAll clusters created successfully!")
            print(
                f"Development cluster: {dev_result['cluster_info']['Endpoint']['Address']}"
            )
            print(
                f"Production cluster: {prod_result['cluster_info']['Endpoint']['Address']}"
            )
            print(
                f"Minimal cluster: {min_result['cluster_info']['ClusterIdentifier']} (creation in progress)"
            )

        else:
            print("Invalid choice. Please run the script again.")
            return

        print("\n" + "=" * 50)
        print("Example completed successfully!")
        print("Remember to clean up resources when you're done to avoid charges.")

    except Exception as e:
        print(f"\nError running example: {e}")
        print("Please check your AWS credentials and permissions.")


if __name__ == "__main__":
    main()
