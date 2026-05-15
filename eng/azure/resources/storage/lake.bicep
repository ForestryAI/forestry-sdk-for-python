param location string

param lakeStorageConfiguration object
param managedIdentityConfiguration object

resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: managedIdentityConfiguration.name
  location: location
}

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: lakeStorageConfiguration.name
  location: location
  sku: {
    name: lakeStorageConfiguration.sdk.name
  }
  kind: 'StorageV2'
  properties: {
    isHnsEnabled: true
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
  }
}

resource telemetriesContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  name: '${storageAccount.name}/default/telemetries'
  properties: {
    publicAccess: 'None'
  }
}

var blobReaderRoleId = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  '2a2b9908-6ea1-4ae2-8e65-a410df84e7d1'
)

resource storageBlobReaderRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(
    storageAccount.id,
    managedIdentity.id,
    blobReaderRoleId
  )

  scope: storageAccount

  properties: {
    principalId: managedIdentity.properties.principalId
    roleDefinitionId: blobReaderRoleId
    principalType: 'ServicePrincipal'
  }
}

output storageAccountName string = storageAccount.name
output storageUrl string = storageAccount.properties.primaryEndpoints.blob
