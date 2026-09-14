-   [Getting Started with Amazon Redshift - AWS Online Tech Talks](https://www.youtube.com/watch?v=dfo4J5ZhlKI)

-   **Agenda**

    -   Challenges of data analytics at scale
    -   Benefits of Amazon Redshift
        -   Introduction
        -   Getting started
        -   Scalability
        -   Security
    -   Live demonstrations
    -   Additional resources
    -   Questions and Answers

-   **Data Arousing Trends**

    -   Migrations to the cloud
        -   Existing on-premise Data Warehouses lack flexibility and scale
        -   High costs associated with maintaining and renewing hardware
    -   New types of data in organizations
        -   Rise of event data
        -   Exponential growth of data outside traditional structured data sources
            -   IoT data
            -   Streaming data
            -   Event data
            -   Log data
        -   Combination of new data sources with traditional structured data

-   **Amazon Redshift Advantages**

    -   Capitalizes on data trends
    -   Helps monetize or derive value from data

-   **Challenges in Analytics at Scale**

    -   Volume, variety, and velocity of data
    -   Enabling access to data across the organization
        -   Performance and concurrency challenges
            -   Dashboard users
            -   Data scientists
            -   Data engineers
        -   Access methods
            -   SQL
            -   Programmatic access (Python, Spark)
            -   BI tools
            -   SQL prompts
    -   Security and governance
        -   Compliance frameworks
        -   Fine-grained control over data
    -   Increasing costs and inflexibility of on-premise systems
        -   Inflexible licensing models (perpetual licenses)
        -   Challenges handling unstructured and machine-generated data

-   **Real-Time Lakehouse Approach**

    -   Combines traditional data sources in a data warehouse with event data in an object store (Amazon S3)
    -   Real-time data in a transactional database (Amazon RDS or Aurora)
    -   Single interface through Redshift queries or dashboards
        -   Tables virtually map to data in S3 or transactional databases
    -   Query Federation Model
        -   Data can be local to Redshift, in S3, or in a Postgres database
        -   Analysts see tables and schemas for easy interaction
    -   Flexibility and scalability for insights across all organizational data

-   **Amazon Redshift Popularity and Benefits**

    -   Most popular cloud data warehouse with tens of thousands of customers
    -   Integration with data lakes and AWS services
        -   AWS Lake Formation
        -   CloudWatch for monitoring
        -   Data Warehouse Migration Service
    -   Best performance
        -   Industry benchmarking
        -   Customer feedback
    -   Lowest cost
        -   Stable and predictable pricing model
    -   Most scalable
        -   Concurrency scaling for variable workloads
    -   Most secure and compliant
        -   Virtual Private Cloud (VPC)
        -   Data encryption options
        -   Compliance certifications (PCI, PSS, FedRAMP)
    -   Easy to manage
        -   Automated optimization features
            -   Automatic table analysis
            -   Automatic vacuum delete
            -   Machine learning-based sorting
        -   Redshift Advisor for tailored recommendations

-   **Amazon Redshift Architecture**

    -   **User Interaction**
        -   SQL clients
        -   BI products (Tableau, MicroStrategy, Qlik)
        -   Data integration products (Informatica, Matillion, Talend)
    -   **Connection**
        -   Leader node using JDBC and ODBC drivers
    -   **Compute Nodes**
        -   Parallel query execution
        -   Integration with Amazon S3
            -   Data copying and unloading in parallel
        -   Redshift Spectrum for querying data in S3
            -   Open formats (CSV, JSON, ORC, Parquet, Avro)
            -   Joining S3 data with local Redshift data
    -   **Optimization and Automation**
        -   Automated table analysis and optimization
        -   Automatic vacuum delete
        -   Machine learning-based sorting recommendations
        -   Redshift Advisor for operational statistics and tailored recommendations

-   **Demo: Creating a Data Warehouse with Amazon Redshift**

    -   Steps to create a cluster
        -   Provide cluster identifier
        -   Select instance type (e.g., RA3)
        -   Specify compute nodes
        -   Configure database settings
        -   Set up IAM role for S3 access
        -   Create cluster
    -   Cluster creation process (takes a few minutes)

-   **Data Modeling and Data Types in Redshift**

    -   Supported data models: Star, Snowflake, Denormalized, Data Vault
    -   Table creation and column definition
    -   Supported data types: Numeric, Text, Date, Time, Geometric, Geospatial
    -   Example: Geospatial data (Airbnb locations in Berlin)

-   **Data Ingestion**

    -   Using the COPY command
        -   Specify bucket, path, location on S3
        -   Provide IAM roles for access
        -   Supported file formats: CSV, Text, JSON, ORC, Parquet, Avro

-   **Materialized Views**

    -   Benefits:
        -   Improved performance for complex queries
        -   Persisted computation for faster query execution
        -   Incremental refresh of views when underlying tables change
    -   Use cases:
        -   Replace complex views
        -   Efficient ETL pipeline performance

-   **Stored Procedures**

    -   Supported in PL/pgSQL format
    -   Use cases:
        -   DDL, DML operations
        -   SELECT queries
    -   Migration tool: AWS Schema Conversion Tool for converting traditional stored procedures

-   **Data Pipeline Integration**

    -   Existing products supporting ODBC or JDBC drivers integrate well
    -   Native AWS services for building data pipelines:
        -   AWS Database Migration Services
        -   AWS Glue
        -   Amazon EMR (Hadoop managed service)
        -   Amazon SageMaker (machine learning)
        -   Amazon QuickSight (visualization and dashboarding)

-   **Demo Overview**

    -   Connecting to the Redshift cluster using Query Editor
    -   Steps:
        -   Creating a schema
        -   Creating a table within the schema
        -   Defining columns and data types
        -   Using the COPY command to load data from S3
        -   Analyzing the data using SQL

-   **Redshift Spectrum**

    -   Extends Redshift to the data lake on S3
    -   Use cases:
        -   Querying Clickstream data in near real-time
        -   ELT processes
        -   Flattening nested JSON datasets
    -   Supported by many BI products

-   **Federated Query**

    -   Run analytical queries on operational data stores (e.g., Aurora Postgres, RDS Postgres)
    -   Join transactional data with data warehouse and data lake data
    -   Create a unified view for end users

-   **Unloading Data**

    -   Using the UNLOAD command to export data from Redshift to S3
    -   Supported formats: CSV, Parquet
    -   Ability to specify partition key for Parquet format

-   **Lakehouse Architecture Demo**

    -   Querying data on S3
    -   Joining S3 data with Redshift data
    -   Analyzing and unloading data back to S3
    -   Using AWS Glue as Hive metastore/catalog

-   **Monitoring and Optimization**

    -   Redshift Console for cluster health and workload monitoring
    -   Redshift Advisor for optimization recommendations
    -   Query Monitoring Dashboard for detailed query analysis

-   **Scalability and Security with Amazon Redshift**

    -   **Elasticity**

        -   Compute elasticity:
            -   Horizontal scaling with Elastic Resize
            -   Vertical scaling with Concurrency Scaling
        -   Concurrency Scaling:
            -   Dynamically scale compute resources based on workload
            -   Billed by the second, one free hour per day
        -   Elastic Resize:
            -   Adjust the base number of compute nodes

    -   **RA3 Nodes with Redshift Managed Storage**

        -   Independent scaling and payment for compute and storage
        -   Efficient data management and consistent performance

    -   **Security**
        -   Comprehensive security features included at no additional cost
        -   Data encryption, IAM and SAML integration, network isolation, auditing, logging
        -   Compliance certifications: SOC 1, 2, 3, FedRAMP, HIPAA
