import argparse
import logging

import uuid
import json

import time
from calendar import monthrange

from datetime import date, datetime, timezone, timedelta

from azure.storage.blob import BlobServiceClient
from azure.data.tables import TableServiceClient
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from azure.identity import DefaultAzureCredential
from azure.core.pipeline.transport import RequestsTransport


# -----------------------------
# Constants
# -----------------------------
reference_map = {
    "received": "FileReceived",
    "duplicate": "FileReceiveDeduplicated",
    "error": "FileWithErrorReceived"
}

machine_map = {
    "mm002010": "sdcgpx0414",
    "mm002020": "sdcgpx3502",
    "mm002045": "sdcgpx2736",
    "mm002051": "sdcgpx2751",
    "mm002053": "sdcgpx2508",
    "mm002054": "sdcgpx3597",
    "mm002077": "sdcgpx0603",
    "mm002079": "sdcgpx0681",
    "mm002113": "sdcgpx2539",
    "mm002115": "sdcgpx2872",
    "mm002125": "sdcgpx0658",
    "mm002133": "sdcgpx4542",
    "mm002182": "sdcgpx1300",
    "mm002192": "sdcgpx2886",
    "mm002233": "sdcgpx1297",
    "mm002275": "sdcgpx1292",
    "mm002288": "sdcgpx2883",
    "mm002301": "sdcgpx8044",
    "mm002318": "sdcgpx6740",
    "mm002328": "sdcgpx3504",
    "mm002336": "sdcgpx5004",
    "mm002365": "sdcgpx3507",
    "mm002374": "sdcgpx9057",
    "mm002376": "sdcgpx4310",
    "mm002378": "sdcgpx5016",
    "mm002401": "sdcgpx0427",
    "mm002403": "sdcgpx4556",
    "mm002404": "sdcgpx1067",
    "mm002406": "sdcgpx5007",
    "mm002412": "sdcgpx5238",
    "mm002415": "sdcgpx5228",
    "mm002422": "sdcgpx8054",
    "mm002426": "sdcgpx3667",
    "mm002427": "sdcgpx5255",
    "mm002428": "sdcgpx3650",
    "mm002431": "sdcgpx3664",
    "mm002439": "sdcgpx3673",
    "mm002440": "sdcgpx5000",
    "mm002444": "sdcgpx5003",
    "mm002446": "sdcgpx3669",
    "mm002447": "sdcgpx7124",
    "mm002449": "sdcgpx7122",
    "mm002465": "sdcgpx7131",
    "mm002466": "sdcgpx7142",
    "mm002473": "sdcgpx2733",
    "mm002477": "sdcgpx2734",
    "mm002484": "sdcgpx3659",
    "mm002486": "sdcgpx7163",
    "mm002489": "sdcgpx2746",
    "mm002490": "sdcgpx7165",
    "mm002491": "sdcgpx7166",
    "mm002496": "sdcgpx7155",
    "mm002499": "sdcgpx4508",
    "mm002501": "sdcgpx5632",
    "mm002503": "sdcgpx5676",
    "mm002504": "sdcgpx5776",
    "mm002516": "sdcgpx4282",
    "mm002517": "sdcgpx4557",
    "mm002521": "sdcgpx5832",
    "mm002524": "sdcgpx5214",
    "mm002528": "sdcgpx5835",
    "mm002529": "sdcgpx5836",
    "mm002530": "sdcgpx4539",
    "mm002532": "sdcgpx6212",
    "mm002533": "sdcgpx5195",
    "mm002534": "sdcgpx5901",
    "mm002536": "sdcgpx4485",
    "mm002540": "sdcgpx6095",
    "mm002542": "sdcgpx5614",
    "mm002549": "sdcgpx6337",
    "mm002553": "sdcgpx5011",
    "mm002554": "sdcgpx6245",
    "mm002555": "sdcgpx6367",
    "mm002556": "sdcgpx4555",
    "mm002559": "sdcgpx4691",
    "mm002561": "sdcgpx4707",
    "mm002564": "sdcgpx6879",
    "mm002567": "sdcgpx5563",
    "mm002568": "sdcgpx5047",
    "mm002569": "sdcgpx7157",
    "mm002572": "sdcgpx4833",
    "mm002576": "sdcgpx0170",
    "mm002578": "sdcgpx5671",
    "mm002584": "sdcgpx3861",
    "mm002586": "sdcgpx0758",
    "mm002589": "sdcgpx4611",
    "mm002590": "sdcgpx3595",
    "mm002596": "sdcgpx3639",
    "mm002598": "sdcgpx6881",
    "mm002599": "sdcgpx5853",
    "mm002600": "sdcgpx4534",
    "mm002603": "sdcgpx6618",
    "mm002605": "sdcgpx2782",
    "mm002607": "sdcgpx5064",
    "mm002610": "sdcgpx5002",
    "mm002612": "sdcgpx4316",
    "mm002614": "sdcgpx0426",
    "mm002619": "sdcgpx5770",
    "mm002622": "sdcgpx2542",
    "mm002626": "sdcgpx6046",
    "mm002648": "sdcgpx6008",
    "mm002649": "sdcgpx7554",
    "mm002650": "sdcgpx4725",
    "mm002652": "sdcgpx7336",
    "mm002653": "sdcgpx6266",
    "mm002655": "sdcgpx6329",
    "mm002656": "sdcgpx6692",
    "mm002657": "sdcgpx6253",
    "mm002658": "sdcgpx7167",
    "mm002660": ""
}


# -----------------------------
# Argument parser
# -----------------------------
parser = argparse.ArgumentParser(
    description="Copy receiving Azure Table metadata to viol2error"
)

def validate_year(value: str) -> int:
    if not value.isdigit() or len(value) != 4:
        raise argparse.ArgumentTypeError("Year must be a 4‑digit number.")
    return int(value)

def validate_month(value: str) -> int:
    if not value.isdigit():
        raise argparse.ArgumentTypeError("Month must be a number.")
    month = int(value)
    if month < 1 or month > 12:
        raise argparse.ArgumentTypeError("Month must be between 1 and 12.")
    return month

def validate_day(value: str) -> int:
    if not value.isdigit():
        raise argparse.ArgumentTypeError("Day must be a number.")
    day = int(value)
    if day < 1 or day > 31:
        raise argparse.ArgumentTypeError("Day must be between 1 and 31.")
    return day

def days_until_month_start(year: int, month: int, day: int) -> int:
    target = date(year, month, day)
    today = date.today()
    delta = today - target
    return delta.days

def validate_status(value: str) -> str:
    allowed = {"received", "duplicate", "error"}
    if value not in allowed:
        raise argparse.ArgumentTypeError("Status must be either: received, duplicate, error")   
    return value  


parser.add_argument("--account", type=str, required=True, help="Azure Storage account name.")
parser.add_argument("--table", type=str, required=True, help="Azure Table name.")
parser.add_argument("--container", type=str, required=True, help="Azure Blob container name.")
parser.add_argument("--insights", type=str, required=True, help="Azure Insights resource name.")
parser.add_argument("--status", type=validate_status, required=True, help="Metadata status.")
parser.add_argument("--year", type=validate_year, required=False, default="2025", help="Year Insights constraint")
parser.add_argument("--month", type=validate_month, required=False, default="12", help="Month Insights constraint")
parser.add_argument("--day", type=validate_day, required=False, default="20", help="Day Insights constraint")

# required
args = parser.parse_args()
account = args.account.strip()
table = args.table.strip()
container = args.container.strip()
insights = args.insights.strip()
status = args.status

# optional
days = days_until_month_start(args.year, args.month, args.day)
days_back = int(days)


# -----------------------------
# Normalize json
# -----------------------------
def normalize_for_json(value):
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat() + "Z"
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


# -----------------------------
# Logging
# -----------------------------
logging.basicConfig(
    filename=f"{account}-{table}.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("requests").setLevel(logging.CRITICAL)
logging.getLogger("azure").setLevel(logging.CRITICAL)
logging.getLogger("botocore").setLevel(logging.CRITICAL)


# -----------------------------
# Azure access
# -----------------------------
credential = DefaultAzureCredential()
transport = RequestsTransport(connection_pool_maxsize=50, keep_alive=True)


# -----------------------------
# Azure Table client
# -----------------------------
account_table_url = f"https://{account}.table.core.windows.net"

table_service_client = TableServiceClient(endpoint=account_table_url, credential=credential, transport=transport)
table_client = table_service_client.get_table_client(table_name=table)


# -----------------------------
# Azure Blob client
# -----------------------------
account_blob_url = f"https://{account}.blob.core.windows.net"
blob_service_client = BlobServiceClient(account_blob_url, credential=credential, transport=transport)


# -----------------------------
# Azure Monitor client
# -----------------------------
insights_client = LogsQueryClient(credential)
insights_workspace_id = "e73191e8-e7ea-475a-a534-9da125a0f44a"

query = f"""
let daysBack = {days_back}d;
let referenceName = "{reference_map[status]}";

AppEvents
    | where TimeGenerated >= now(-daysBack)
    | where Name == "FileReceivedMetadata"
    | extend dimensions = parse_json(Properties)
    | extend row_key = tostring(dimensions["correlationId"])
    | extend fileName = tostring(dimensions["filename"])
    | extend fileNameSegments = split(fileName, "-")    
    | order by TimeGenerated desc
    | project actor = tostring(fileNameSegments[0]), machine = tostring(fileNameSegments[1]), row_key, OperationId
"""


# -----------------------------
# Transfer
# -----------------------------
end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(days=days_back)

used = 0
start = time.time()
continuation = None

mm_machines = set()

while start_time < end_time:
    take_time = start_time + timedelta(days=1)
    logging.info(f"starting: {start_time}, taking: {take_time}, ending: {end_time}")

    if continuation:
        response = insights_client.query_workspace(
            workspace_id=insights_workspace_id,
            query=query,
            timespan=(start_time, take_time),
            continuation_token=continuation
        )
    else: 
        response = insights_client.query_workspace(
            workspace_id=insights_workspace_id,
            query=query,
            timespan=(start_time, take_time)
        )

    if response.status != LogsQueryStatus.SUCCESS:
        logging.error(f"Query status: {response.status}, page: {take_time}")
        raise RuntimeError(f"Query failed: {response.status}")
    
    for table in response.tables:
        columns = table.columns
        for row in table.rows:
            actor = row[0]
            machine = row[1]

            row_key = row[2]

            if actor == "gpx107" and machine.startswith("mm"):
                mm_machines.add(machine);

            used += 1

    # get partition_key, row_key then call Azure Table
    # use Azure Table entity to create Azure Blob

    continuation = getattr(response, "continuation_token", None)
    if continuation:
        # More pages for this day — continue paging
        continue
    
    # No continuation → finished this day → move to next day
    start_time = take_time
    continuation = None


# -----------------------------
# Results
# -----------------------------
elapsed = time.time() - start

logging.info(f"Total entities processed: {used}")
logging.info(f"Days used: {days_back}")
logging.info(f"Total time: {elapsed:.2f} seconds\n")
for machine in sorted(mm_machines):
    logging.info(f"  {machine}")