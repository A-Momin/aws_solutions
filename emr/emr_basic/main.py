import argparse

from pyspark.sql import SparkSession
from pyspark.sql import functions as fn

def transform_data(data_source, output_uri):
    with SparkSession.builder.appName('test_emr').getOrCreate() as spark:
        df = spark.read.option('header', 'true').csv(data_source)
        df = df.select(
            fn.col("Name").alias("name"),
            fn.col("Violation Type").alias("violation_type")
        )
        df.createOrReplaceTempView("restaurant_violations")
        GROUP_BY_QUERY = """SELECT name, count(*) as total_red_violations FROM restaurant_violations WHERE violation_type == "RED" GROUP BY name"""
        transformed_df = spark.sql(GROUP_BY_QUERY)
        print(f"Number of Rows in SQL Query {transformed_df.count()}")
        transformed_df.write.mode("overwrite").parquet(output_uri)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_source")
    parser.add_argument("--output_uri")

    args = parser.parse_args()

    transform_data(args.data_source, args.output_uri)