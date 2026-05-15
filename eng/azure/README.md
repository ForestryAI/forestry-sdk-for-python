# Azure tenent and subscription
Both the Azure tenent "**Foresty-AI*** and subscription **forestry** are important when using the Azure CLI (see Microsoft [information](https://learn.microsoft.com/en-us/cli/azure/manage-azure-subscriptions-azure-cli?view=azure-cli-latest&tabs=bash)).

All active tenents can be listed with:
```
az account tenant list
```

then tenant identity is established with:
```
az login --tenant {tenant-id} --use-device-code
```

where the ```--use-device-code``` is optional when running locally i.e. outside a pipeline.  An active subscription can be set by name:
```
$subscriptionName="forestry"

az account set --subscription $subscriptionName
```

## Resource group
A resource group is created (see Microsoft [information](https://learn.microsoft.com/en-us/cli/azure/group?view=azure-cli-latest#az-group-create)) with the Azure CLI in PowerShell:
```
$environment="poc"
$resourceGroup="rg-forestry-$environment"

az group create \
  --name $resourceGroup \
  --location swedencentral
```

where the only environment currently is ```poc```.  

## Deployment
Once the resource group exists then everything else is done by Azure CLI deployment (see Microsoft [information](https://learn.microsoft.com/en-us/azure/azure-resource-manager/templates/deploy-cli?toc=%2Fcli%2Fazure%2Ftoc.json&bc=%2Fcli%2Fazure%2Fbreadcrumb%2Ftoc.json&view=azure-cli-latest)):
```
az deployment group create \
  --resource-group $resourceGroup \
  --template-file main.bicep \
  --parameters environments/poc/main.bicepparam
```

from this directory.

## Kusto extension
The Azure CLI has extensions which can be listed by:
```
az extension list --output table
```

The Kusto extension is useful when needing to run KQL queries from the command line:
```
az extension add --name kusto
```

## ADX portal
The ADX cluster has a portal:
```
https://adx-forestry-poc.swedencentral.kusto.windows.net
```

The user running the Bicep deployment needs to have super ADX access otherwise policies can not be created.