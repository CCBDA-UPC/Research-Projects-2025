import boto3

athena = boto3.client('athena', region_name='us-east-1')  

database_name = "mydata"
output_location = "s3://my-bucket-20250508/athena-results/"  # Replace with your bucket

def run_query(query, database=None):
    params = {
        'QueryString': query,
        'ResultConfiguration': {'OutputLocation': output_location}
    }
    if database:
        params['QueryExecutionContext'] = {'Database': database}
    
    response = athena.start_query_execution(**params)
    return response['QueryExecutionId']

def wait_for_query(query_execution_id):
    while True:
        result = athena.get_query_execution(QueryExecutionId=query_execution_id)
        state = result['QueryExecution']['Status']['State']
        if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            break

# Step 1: Create the database (if not exists)
create_db_query = f"CREATE DATABASE IF NOT EXISTS {database_name};"
wait_for_query(run_query(create_db_query, database=None))

# Step 2: Create the table
create_table_query = """
CREATE EXTERNAL TABLE IF NOT EXISTS customers (
  idx INT,
  customer_id STRING,
  first_name STRING,
  last_name STRING,
  company STRING,
  city STRING,
  country STRING,
  phone1 STRING,
  phone2 STRING,
  email STRING,
  subscription_date STRING,
  website STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
  "separatorChar" = ",",
  "quoteChar" = "\\""
)
LOCATION 's3://my-bucket-20250508/'  -- replace with actual bucket path
TBLPROPERTIES ('skip.header.line.count'='1');
"""
wait_for_query(run_query(create_table_query))

print("Database and table created successfully.")