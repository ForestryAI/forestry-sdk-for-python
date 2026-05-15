param location string

param adxClusterConfiguration object
param managedIdentityConfiguration object

resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: managedIdentityConfiguration.name
  location: location
}

resource adxCluster 'Microsoft.Kusto/clusters@2023-08-15' = {
  name: adxClusterConfiguration.name
  location: location
  sku: {
    name: adxClusterConfiguration.sdk.name
    tier: adxClusterConfiguration.sdk.tier
    capacity: adxClusterConfiguration.sdk.capacity
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentity.id}': {}
    }
}
  properties: {
    enableStreamingIngest: true
  }
}

resource adxDatabase 'Microsoft.Kusto/clusters/databases@2023-08-15' = {
  parent: adxCluster
  name: adxClusterConfiguration.databaseName
  location: location
  kind: 'ReadWrite'
  properties: {
    softDeletePeriod: 'P365D'
    hotCachePeriod: 'P31D'
  }
}

resource clusterIdentity 'Microsoft.Kusto/clusters/principalAssignments@2023-08-15' = {
  name: 'cluster-mi-assignment'
  parent: adxCluster
  properties: {
    principalId: managedIdentity.properties.principalId
    role: 'AllDatabasesAdmin'
    tenantId: subscription().tenantId
    principalType: 'App'
  }
}

resource managedIdentityPolicy 'Microsoft.Kusto/clusters/databases/scripts@2023-08-15' = {
  parent: adxDatabase
  name: 'managed-identity-policy'
  properties: {
    scriptContent: '.alter-merge database ${adxClusterConfiguration.databaseName} policy managed_identity \'[{"ObjectId": "${managedIdentity.properties.principalId}", "AllowedUsages": "ExternalTable"}]\''
    continueOnErrors: false
  }
}

output adxClusterUri string = adxCluster.properties.uri
output adxDatabase string = adxDatabase.name
