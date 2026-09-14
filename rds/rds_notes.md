#### Create RDS Database

Endpoint: rdsmysql1.cdeemgug4meu.us-east-1.rds.amazonaws.com
Port: 3306

### Migration of Database in EC2 Instance to RDS Database:

-   Dump database schema from my **local** mysql database

    -   `$ mysqldump -u Shah -p interview_questions > interview_questions.sql`

-   Load data into `interview_questions` database of AWS RDS instance

    -   `$ mysql -h httx-rds-mysql.cdeemgug4meu.us-east-1.rds.amazonaws.com -P 3306 -u httxadmin -p interview_questions < interview_questions.sql`
    -   `$ psql -h httx-rds-postgresql.cdeemgug4meu.us-east-1.rds.amazonaws.com -p 5432 -U httxadmin -d interview_questions < interview_questions.sql`

-   login to AWS RDS instance

    -   `$ mysql -h httx-rds-mysql.cdeemgug4meu.us-east-1.rds.amazonaws.com -P 3306 -u httxadmin -p`
    -   `$ psql -h httx-rds-postgresql.cdeemgug4meu.us-east-1.rds.amazonaws.com -p 5432 -U httxadmin -d interview_questions`
    -   `mysql> SELECT VERSION();`

```json
{'DBInstanceIdentifier': 'mysqlrds1',
 'DBInstanceClass': 'db.t4g.micro',
 'Engine': 'mysql',
 'DBInstanceStatus': 'available',
 'MasterUsername': 'httxadmin',
 'Endpoint': {'Address': 'httx-rds-mysql.cdeemgug4meu.us-east-1.rds.amazonaws.com',
  'Port': 3306,
  'HostedZoneId': 'Z2R2ITUGPM61AM'},
 'AllocatedStorage': 20,
 'InstanceCreateTime': datetime.datetime(2024, 9, 15, 18, 2, 56, 205000, tzinfo=tzutc()),
 'PreferredBackupWindow': '07:26-07:56',
 'BackupRetentionPeriod': 0,
 'DBSecurityGroups': [],
 'VpcSecurityGroups': [{'VpcSecurityGroupId': 'sg-078c21a84bcce4ba5',
   'Status': 'active'}],
 'DBParameterGroups': [{'DBParameterGroupName': 'default.mysql8.0',
   'ParameterApplyStatus': 'in-sync'}],
 'AvailabilityZone': 'us-east-1b',
 'DBSubnetGroup': {'DBSubnetGroupName': 'rds-glue-sg-group',
  'DBSubnetGroupDescription': 'rds-glue-sg-group',
  'VpcId': 'vpc-09de973c80208055f',
  'SubnetGroupStatus': 'Complete',
  'Subnets': [{'SubnetIdentifier': 'subnet-03f1973d27ecf675d',
    'SubnetAvailabilityZone': {'Name': 'us-east-1a'},
    'SubnetOutpost': {},
    'SubnetStatus': 'Active'},
   {'SubnetIdentifier': 'subnet-09f83820ceae7af84',
    'SubnetAvailabilityZone': {'Name': 'us-east-1b'},
    'SubnetOutpost': {},
    'SubnetStatus': 'Active'}]},
 'PreferredMaintenanceWindow': 'fri:05:02-fri:05:32',
 'PendingModifiedValues': {},
 'MultiAZ': False,
 'EngineVersion': '8.0.32',
 'AutoMinorVersionUpgrade': False,
 'ReadReplicaDBInstanceIdentifiers': [],
 'LicenseModel': 'general-public-license',
 'Iops': 3000,
 'OptionGroupMemberships': [{'OptionGroupName': 'default:mysql-8-0',
   'Status': 'in-sync'}],
 'PubliclyAccessible': True,
 'StorageType': 'gp3',
 'DbInstancePort': 0,
 'StorageEncrypted': False,
 'DbiResourceId': 'db-YTRVKU3IFIZHLJGQDY6WZ22TKY',
 'CACertificateIdentifier': 'rds-ca-rsa2048-g1',
 'DomainMemberships': [],
 'CopyTagsToSnapshot': True,
 'MonitoringInterval': 0,
 'DBInstanceArn': 'arn:aws:rds:us-east-1:381492255899:db:mysqlrds1',
 'IAMDatabaseAuthenticationEnabled': False,
 'PerformanceInsightsEnabled': False,
 'DeletionProtection': False,
 'AssociatedRoles': [],
 'MaxAllocatedStorage': 1000,
 'TagList': [],
 'CustomerOwnedIpEnabled': False,
 'ActivityStreamStatus': 'stopped',
 'BackupTarget': 'region',
 'NetworkType': 'IPV4',
 'StorageThroughput': 125,
 'CertificateDetails': {'CAIdentifier': 'rds-ca-rsa2048-g1',
  'ValidTill': datetime.datetime(2025, 9, 15, 18, 2, 7, tzinfo=tzutc())},
 'DedicatedLogVolume': False,
 'IsStorageConfigUpgradeAvailable': False,
 'EngineLifecycleSupport': 'open-source-rds-extended-support-disabled'}
```
