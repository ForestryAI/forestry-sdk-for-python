param environment string
param workload string
param location string

param storageSkuName string

param adxSkuCapacity int
param adxSkuName string
param adxSkuTier string

param adxDatabaseName string

var storageAccountName = 'st${workload}${environment}'
var adxClusterName = 'adx-${workload}-${environment}'

module adx './resources/adx/cluster.bicep' = {
  name: 'adx'
  params: {
    location: location

    adxClusterName: adxClusterName
    adxSkuCapacity: adxSkuCapacity
    adxSkuName: adxSkuName
    adxSkuTier: adxSkuTier

    adxDatabaseName: adxDatabaseName
  }
}

module lake './resources/storage/lake.bicep' = {
  name: 'lake'
  params: {
    storageAccountName: storageAccountName
    location: location
    storageSkuName: storageSkuName

    adxPrincipalId: adx.outputs.principalId
  }
}

module externalTables './resources/adx/tables.bicep' = {
    name: 'externalTables'
    params: {
        storageUrl: lake.outputs.storageUrl
        adxClusterName: adxClusterName
        adxDatabaseName: adxDatabaseName
    }
}
