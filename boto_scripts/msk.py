import boto3, botocore
from botocore.exceptions import ClientError
import os, time, json, io, zipfile
from datetime import date

# ==============================================================================
# boto3.setup_default_session(profile_name="AMominNJ")
ACCOUNT_ID        = os.environ['AWS_ACCOUNT_ID_ROOT']
REGION            = os.environ['AWS_DEFAULT_REGION']
VPC_ID            = os.environ['AWS_DEFAULT_VPC']
SECURITY_GROUP_ID = os.environ['AWS_DEFAULT_SG_ID']
SUBNET_IDS        = SUBNET_IDS = os.environ["AWS_DEFAULT_SUBNET_IDS"].split(":")
SUBNET_ID         = SUBNET_IDS[0]

ec2_client   = boto3.client('ec2', region_name=REGION)
ec2_resource = boto3.resource('ec2', region_name=REGION)
msk_client   = boto3.client('kafka')

# ==============================================================================

def create_msk_cluster(ClusterName, ClientSubnets, SecurityGroups):
    try:
        response = msk_client.create_cluster(
            ClusterName=ClusterName,  # Replace with your desired cluster name
            KafkaVersion='3.5.1',  # Replace with your desired Kafka version
            NumberOfBrokerNodes=2,  # Default number of brokers is 3
            BrokerNodeGroupInfo={
                'BrokerAZDistribution': 'DEFAULT',  # Distribute brokers across availability zones
                'InstanceType': 'kafka.t3.small', # Default broker instance type is 'kafka.m5.large' | ProvisionedThroughput is not supported for 'kafka.t3.small'
                'ClientSubnets': ClientSubnets,
                'SecurityGroups': SecurityGroups,
                'StorageInfo': {
                    'EbsStorageInfo': {
                        # 'ProvisionedThroughput': {
                        #     'Enabled': True,
                        #     'VolumeThroughput': 250
                        # },
                        'VolumeSize': 10  # Default EBS volume size is 100 in GiB
                    }
                }
            },
            # ConfigurationInfo={
            #     'Arn': 'string',
            #     'Revision': 123
            # },
            ClientAuthentication={
                # 'Sasl': {
                #     'Scram': {
                #         'Enabled': False
                #     },
                #     'Iam': {
                #         'Enabled': False
                #     }
                # },
                # 'Tls': {
                #     'CertificateAuthorityArnList': [
                #         'string',
                #     ],
                #     'Enabled': False
                # },
                'Unauthenticated': {
                    'Enabled': True # Allow unauthorized access
                }
            },
            EncryptionInfo={
                # 'EncryptionAtRest': {         # by default available
                #     'DataVolumeKMSKeyId': 'string'
                # },
                'EncryptionInTransit': {
                    'ClientBroker': 'TLS_PLAINTEXT',  # Encryption between clients and brokers (default is TLS)
                    'InCluster': True
                }
            },
            EnhancedMonitoring='DEFAULT',  # Monitoring level
            OpenMonitoring={
                'Prometheus': {
                    'JmxExporter': {
                        'EnabledInBroker': False  # Default JMX exporter configuration
                    },
                    'NodeExporter': {
                        'EnabledInBroker': False  # Default Node exporter configuration
                    }
                }
            },
            LoggingInfo={
                'BrokerLogs': {
                    'CloudWatchLogs': {
                        'Enabled': False
                    },
                    'Firehose': {
                        'Enabled': False
                    },
                    'S3': {
                        'Enabled': False
                    }
                }
            },
            Tags={
                'Environment': 'httx-test-MSK'  # Add your tags here
            }
        )

        print("Cluster creation initiated:", response)

        return response

    except Exception as e:
        print("Error creating MSK cluster:", str(e))


