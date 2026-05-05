import argparse
import calendar
import logging

from datetime import datetime, timezone
from collections import defaultdict, Counter

import sys

from azure.data.tables import TableServiceClient
from azure.identity import DefaultAzureCredential
from azure.core.pipeline.transport import RequestsTransport


# -----------------------------
# Month parser (numeric or name)
# -----------------------------
def parse_month(value: str) -> int:
    v = value.lower()

    # Numeric month
    if v.isdigit():
        m = int(v)
        if 1 <= m <= 12:
            return m
        raise argparse.ArgumentTypeError("Month must be 1–12")

    # Month names
    for i in range(1, 13):
        if v == calendar.month_name[i].lower() or v == calendar.month_abbr[i].lower():
            return i

    raise argparse.ArgumentTypeError("Invalid month. Use 1–12 or a month name.")


# -----------------------------
# Argument parser
# -----------------------------
parser = argparse.ArgumentParser(
    description="Maximum identity creation frequency per second per domain for a given month"
)

parser.add_argument("--account", type=str, required=True, help="Azure Table Storage account name.")
parser.add_argument("--table", type=str, required=True, help="Azure Table name.")
parser.add_argument("--year", type=int, help="Year, e.g. 2026")
parser.add_argument("--month", type=parse_month, help="Month, e.g. 1 or January")

args = parser.parse_args()
account = args.account.strip()
table = args.table.strip()

now = datetime.now(timezone.utc)

# Default to current month/year
year = args.year if args.year else now.year
month = args.month if args.month else now.month


# -----------------------------
# Logging
# -----------------------------
logging.basicConfig(
    filename=f"{account}-{table}-{year}-{month:02d}.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("requests").setLevel(logging.CRITICAL)
logging.getLogger("azure").setLevel(logging.CRITICAL)
logging.getLogger("botocore").setLevel(logging.CRITICAL)


# -----------------------------
# Compute month window
# -----------------------------
start = datetime(year, month, 1, tzinfo=timezone.utc)

# First day of next month
if month == 12:
    end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
else:
    end = datetime(year, month + 1, 1, tzinfo=timezone.utc)

# Warn if using partial current month
if year == now.year and month == now.month:
    days_used = (now - start).days + 1
    logging.warning(f"Using only the first {days_used} days of the current month.")


# -----------------------------
# Azure Table client
# -----------------------------
account_url = f"https://{account}.table.core.windows.net"
credential = DefaultAzureCredential()

transport = RequestsTransport(connection_pool_maxsize=50, keep_alive=True)

client = TableServiceClient(endpoint=account_url, credential=credential, transport=transport)
table_client = client.get_table_client(table_name=table)


# -----------------------------
# Scan table
# -----------------------------
used = 0
skipped = 0
freq = defaultdict(Counter)

logging.info(f"Time window: {start} to {end}")
for entity in table_client.list_entities(select=["Updated", "Domain"]):
    timestamp = entity.get("Updated")
    domain = sys.intern(entity.get("Domain"))

    # Only timestamps inside the month window
    if not (start <= timestamp < end):
        skipped += 1
        if skipped % 1000000 == 0:
            logging.warning(f"Skipped {skipped} entities of {used} used. Continuing to process...")
            logging.info("Current timestamp type: %s; value: %r", type(timestamp), timestamp)
        continue

    # Only weekdays
    if timestamp.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        skipped += 1
        if skipped % 1000000 == 0:
            logging.warning(f"Skipped {skipped} entities of {used} used. Continuing to process...")
            logging.info("Current timestamp type: %s; value: %r", type(timestamp), timestamp)
        continue

    # Only between 6 AM and 6 PM UTC
    if not (6 <= timestamp.hour < 18):
        skipped += 1
        if skipped % 1000000 == 0:
            logging.warning(f"Skipped {skipped} entities of {used} used. Continuing to process...")
            logging.info("Current timestamp type: %s; value: %r", type(timestamp), timestamp)
        continue

    used += 1

    second_key = int(timestamp.timestamp())
    freq[domain][second_key] += 1



# -----------------------------
# Compute average second per domain
# -----------------------------
averagePerDomain = {}

for domain, seconds in freq.items():
    total = sum(seconds.values()) 
    distinct_seconds = len(seconds) 
    average = total / distinct_seconds if distinct_seconds else 0

    averagePerDomain[domain] = {
        "average_per_second": average, 
        "total_events": total, 
        "seconds_counted": distinct_seconds
    }


# -----------------------------
# Results
# -----------------------------
logging.info(f"Total entities processed: {used}")
logging.info(f"Total entities skipped: {skipped}")

for domain, info in averagePerDomain.items():
    logging.info( 
        "%s: average = %.4f creations/sec over %d seconds (%d total events)", 
        domain, 
        info["average_per_second"], 
        info["seconds_counted"], 
        info["total_events"] 
    )
