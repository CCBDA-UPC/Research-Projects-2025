## About our problems with Glue + RDS

In a previous version of this document, Glue was used as an ETL tool to extract data from both the PostgreSQL RDS database, containing `leads`, `feeds` and `article_hits`, and a CSV file inside an S3 bucket, containing some personal information about the leads - mainly, their country of origin - which would demonstrate the capacity of the system to handle data from different sources. On top of that, in that version, instead of dumping the output data into Parquet files in S3, we were loading it into a properly designed Data Warehouse in RDS.

However, we encountered several problems when trying to connect Glue to the RDS databases. So, here's the process of connecting Glue to RDS, and the problems we encountered along the way:

### Previous work: Creating the Data Warehouse in RDS

Previous to everything, we created an RDS instance with PostgreSQL which would be used as our Data Warehouse. This process has been done tons of times, so we won't go into detail about it.

### Creating the Glue Connections

Before creating the Tables in the Catalog, we needed to define the connections to the RDS service that were to be used by Glue. This is done in the AWS Console, under the Glue service.

We created two connections, one for the "Operational" database (the one with the `leads`, `feeds` and `article_hits` tables) and another one for the "Data Warehouse" database (the one we created in the previous step).

Here, we encountered our first problem. When defining connections, the first step is to define which type of connection to use. There are a ton of options, but the one we needed was the "PostgreSQL" connection. We selected it, configured it to use **username and password** authentication, and set the connection properties. However, when we tried to connect, we kept on getting the following error:

```
Test connection failed due to: ValidationException. ConnectionStatus is not READY for connection: Form Operational Database Connection
```

When we investigated further, we found out that the console wasn't saving our connection method preference, and was defaulting to "IAM" authentication, even though we had selected "username and password" before. We tried several times, but the console kept on defaulting to "IAM" authentication.

Thus, we defaulted to using a generic JDBC connection, which we configured to use the same connection properties as the PostgreSQL connection. The connection created, and its status changed to "Ready" after a few minutes. However, when we tried the connection (Actions > Test connection), we got the following error:

```
InvalidInputException: VPC S3 endpoint validation failed for SubnetId: subnet-05ae0671a7dc3cf68. VPC: vpc-042ffdd9c80c2701d. Reason: Could not find S3 endpoint or NAT gateway for subnetId: subnet-05ae0671a7dc3cf68 in Vpc vpc-042ffdd9c80c2701d
```

This error was a bit confusing, as, for starters, we were not trying to connect to S3, but to RDS. However, after some investigation, we found the possible explanation of this error:

### Why do JDBC connections fail?

We discovered that the JDBC connection tries to connect to the database using the public IP address of the RDS instance. Thus, we need to allow the connection security group to access the RDS one. This means:

1. The Glue connection must be in a private subnet that has access to the internet via a NAT gateway.
2. The RDS connection must allow access from the Glue connection security group.

Even though we were using a public Subnet to execute the Glue connections (thus, it already had access to the internet), we tried to create a NAT gateway in the same Subnet, but the connection kept failing. We thought of creating a new private subnet, but this posed a new problem: The VPC that we've got provisioned in the AWS Learner Lab Account has already several subnets, which span across all the CIDR block of the VPC. Thus, no more subnets can be created.

We attempted to create a Gateway endpoints for S3, for the RDS, and even interfaces for both, but the connection kept failing.
Thus, we figured that the first thing that the connection does is to check if it is being executed in a private subnet with a NAT gateway, and when it doesn't find one, it fails.

Finally, we also tried to search for differences in IAM Policies between what we had and what the AWS official documentation had, but we ditched that idea, as we wouldn't have been able to change them anyway (Learner Lab account doesn't allow Policy changes).

### What would have we done?

If we had been able to connect to the databases, the typical process would have been as follows:

1. Create a Glue connection to the two RDS databases (Operational and Data Warehouse).
2. Create a Glue Database named `operational` which would group tables from the Operational fields, and another one named `data_warehouse` which would group tables from the Data Warehouse.
3. Create several Glue Crawlers: `leads`, `feeds` and `article_hits` would crawl their corresponding tables in the Operational RDS database, and create Catalog Tables inside the `operational` Catalog Database; and `article_hits`, `users` and `articles` would crawl their corresponding tables in the Data Warehouse RDS database and create the Catalog Tables inside the `data_warehouse` Catalog Database.

> [!NOTE]
> Crawlers read the data from the tables they are crawling, and create or update the Catalog Tables with the schema of the data they read. This means that if we add a new column to a table, we can run the Crawler again and it will update the Catalog Table with the new column.

4. Create the table `user_data` in the `data_warehouse` Catalog Database, which would contain the schema and connection details of the CSV file in S3.
5. Create a Glue ETL job similar to the one we created, but with three different target nodes:
    - The `users` table in the Data Warehouse RDS database.
    - The `article_hits` table in the Data Warehouse RDS database.
    - The `user_data` table in the Data Warehouse RDS database.

### References

- [Adding an AWS Glue connection](https://docs.aws.amazon.com/glue/latest/dg/console-connections.html)
- [Setting up VPC for JDBC connections to Amazon RDS from AWS Glue](https://docs.aws.amazon.com/glue/latest/dg/setup-vpc-for-glue-access.html)