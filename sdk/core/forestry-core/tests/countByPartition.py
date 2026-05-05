import argparse
import time
from collections import defaultdict

from azure.data.tables import TableServiceClient
from azure.identity import DefaultAzureCredential

import logging

# Argument parser setup
parser = argparse.ArgumentParser(description="Count entities by partition key in an Azure Table.")
parser.add_argument("--account", type=str, required=True, help="Azure Table Storage account name.")
parser.add_argument("--table", type=str, required=True, help="Azure Table name.")

args = parser.parse_args()
account = args.account.strip()
table = args.table.strip()


# Logging
logging.basicConfig(
    filename=f"{account}-{table}.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.getLogger("urllib3").setLevel(logging.CRITICAL) 
logging.getLogger("requests").setLevel(logging.CRITICAL) 
logging.getLogger("azure").setLevel(logging.CRITICAL) 
logging.getLogger("botocore").setLevel(logging.CRITICAL)


# Set up Azure Table Service Client
account_url = f"https://{account}.table.core.windows.net"
credential = DefaultAzureCredential()
client = TableServiceClient(endpoint=account_url, credential=credential)
table_client = client.get_table_client(table_name=table)


# Count entities by partition key
start = time.time()

partition_counts = defaultdict(int)
seen_partitions = set()
total_entities = 0

print(f"Counting entities in table '{table}' of account '{account}'...\n")
for entity in table_client.list_entities(select="PartitionKey"):
    partition_key = entity["PartitionKey"]

    # Detect new partition keys
    if partition_key not in seen_partitions:
        seen_partitions.add(partition_key)
        # print(f"\nDetected new partition key: {partition_key}")

    # Increment count for this partition key
    partition_counts[partition_key] += 1
    total_entities += 1

    # Optional live per-partition row count
    # print(f" {partition_key}: {partition_counts[partition_key]} rows", end="\r")

elapsed = time.time() - start

print("\n\nTotal entities:", total_entities)


# Log final counts per partition key
logging.info(f"Total entities: {total_entities}") 
logging.info(f"Total partitions: {len(seen_partitions)}") 
logging.info(f"Total time: {elapsed:.2f} seconds\n")

for pk, cnt in sorted(partition_counts.items(), key=lambda x: x[1], reverse=True): 
    logging.info(f" {pk}: {cnt}")