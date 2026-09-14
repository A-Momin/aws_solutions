
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

CATALOG_DB_NAME = 'httx-catalog-db'
S3_BUCKET_DATALAKE = "httx-datalake-bkt"

glueContext = GlueContext(SparkContext.getOrCreate())

customersDF = glueContext.create_dynamic_frame.from_catalog(
             database=CATALOG_DB_NAME,
             table_name="raw_employees")

glueContext.write_dynamic_frame.from_options(
    customersDF, 
    connection_type = "s3", 
    connection_options = {"path": f"s3://{S3_BUCKET_DATALAKE}/cleansed/employees"}, 
    format = "parquet"
)
