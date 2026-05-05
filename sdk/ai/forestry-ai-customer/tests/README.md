# Forestry AI Customer tests for Pythong

This directory contains the **live-service and recorded tests** for the Forestry AI Customer client library.

## Getting started

These instructions assume you are working on Windows, have
Python 3.9 or later, and want to run the tests against **live service
end-points** using a locally built wheel.

### Clone and prepare the SDK repo

```bash
git clone https://sdctfs@dev.azure.com/sdctfs/Labs%20plattform/_git/Forestry-sdk-for-python
cd Forestry-sdk-for-python/sdk/ai/Forestry-ai-customer
```

### Install development dependencies

```bash
pip install -r dev_requirements.txt
```

### Build and install the library locally

```bash
pip install wheel
python setup.py bdist_wheel
pip install dist/Forestry_ai_customer-*.whl --force-reinstall --user
```