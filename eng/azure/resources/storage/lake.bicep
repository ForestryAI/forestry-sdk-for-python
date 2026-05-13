param location string

param storageAccountName string
param storageSkuName string

param adxPrincipalId string

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: storageSkuName
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

resource storageBlobReaderRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(
    storageAccount.id,
    adxPrincipalId,
    'Storage Blob Data Reader'
  )

  scope: storageAccount

  properties: {
    principalId: adxPrincipalId
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '2a2b9908-6ea1-4ae2-8e65-a410df84e7d1'
    )
    principalType: 'ServicePrincipal'
  }
}

output storageAccountName string = storageAccount.name
output storageUrl string = 'https://${storageAccount.name}.${environment().suffixes.storage}/telemetries'
