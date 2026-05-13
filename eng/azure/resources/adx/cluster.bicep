param location string

param adxClusterName string
param adxSkuCapacity int
param adxSkuName string
param adxSkuTier string

param adxDatabaseName string

resource adxCluster 'Microsoft.Kusto/clusters@2023-08-15' = {
  name: adxClusterName
  location: location
  sku: {
    name: adxSkuName
    tier: adxSkuTier
    capacity: adxSkuCapacity
  }
  properties: {
    enableStreamingIngest: true
  }
}

resource adxDatabase 'Microsoft.Kusto/clusters/databases@2023-08-15' = {
  parent: adxCluster
  name: adxDatabaseName
  location: location
  kind: 'ReadWrite'
  properties: {
    softDeletePeriod: 'P365D'
    hotCachePeriod: 'P31D'
  }
}

output adxClusterUri string = adxCluster.properties.uri
output adxDatabase string = adxDatabase.name
output principalId string = adxCluster.identity.principalId
