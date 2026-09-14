import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

CATALOG_DB_NAME = 'httx-catalog-db'
S3_BUCKET_DATALAKE = "httx-datalake-bkt"
S3_BUCKET_GLUE_ASSETS = "httx-glue-assets-bkt"
TEM_DIR = f"s3://{S3_BUCKET_GLUE_ASSETS}/temporary/"

glueContext = GlueContext(SparkContext.getOrCreate())

customerDF = glueContext.create_dynamic_frame.from_catalog(
             database=CATALOG_DB_NAME,
             table_name="source_employee_db_employee", redshift_tmp_dir=TEM_DIR)

glueContext.write_dynamic_frame.from_options(
    customerDF, 
    connection_type = "s3", 
    connection_options = {"path": f"s3://{S3_BUCKET_DATALAKE}/raw/employees"}, 
    format = "csv"
)
