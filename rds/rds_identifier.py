import boto3
import json
import yaml
from datetime import datetime

def get_rds_instance_parameters(instance_identifier):
    rds = boto3.client('rds')
    
    # Describe the RDS instance
    response = rds.describe_db_instances(
        DBInstanceIdentifier=instance_identifier
    )
    
    if response['DBInstances']:
        return response['DBInstances'][0]
    else:
        raise Exception(f'No RDS instance found with identifier {instance_identifier}')

def datetime_serializer(o):
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError(f"Type {type(o)} not serializable")

def main():
    instance_identifier = 'mysqlrds'
    instance_parameters = get_rds_instance_parameters(instance_identifier)
    
    # Convert to JSON
    json_format = json.dumps(instance_parameters, indent=4, default=datetime_serializer)
    print("JSON format:")
    print(json_format)
    
    # Convert to YAML
    yaml_format = yaml.dump(instance_parameters, default_flow_style=False)
    print("\nYAML format:")
    print(yaml_format)

    # Write YAML to file
    with open('rds_instance_parameters.yaml', 'w') as file:
        yaml.dump(instance_parameters, file, default_flow_style=False)

if __name__ == "__main__":
    main()
