from unittest.mock import Mock, patch

import pytest
from dotenv import load_dotenv, find_dotenv

if not load_dotenv(find_dotenv(filename="forestry_ai_customer_tests.env"), override=True):
    print("Failed to apply environment variables for Forestry_ai_customer tests.")

class SanitizedValues:
    TENANT_ID = "00000000-0000-0000-0000-000000000000"
    CLIENT_ID = "00000000-0000-0000-0000-000000000000"


@pytest.fixture(scope="session")
def mock_project_scope():
    return {
        "tenant_id": f"{SanitizedValues.TENANT_ID}",
        "client_id": f"{SanitizedValues.CLIENT_ID}",
    }

    