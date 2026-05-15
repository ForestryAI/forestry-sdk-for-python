param location string

type AdxClusterConfiguration = {
  sdk: {
     name: string
     tier: string
     capacity: int
  }
  databaseName: string
  name: string
}

type LakeStorageConfiguration = {
  sdk: {
    name: string
  }
  name: string
}

type ManagedIdentityConfiguration = {
  name: string
}

param adxClusterConfiguration AdxClusterConfiguration
param lakeStorageConfiguration LakeStorageConfiguration
param managedIdentityConfiguration  ManagedIdentityConfiguration

resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: managedIdentityConfiguration.name
  location: location
}

module adx './resources/adx/cluster.bicep' = {
  name: 'adx'
  params: {
    location: location

    adxClusterConfiguration: adxClusterConfiguration
    managedIdentityConfiguration: managedIdentityConfiguration
  }
}

module lake './resources/storage/lake.bicep' = {
  name: 'lake'
  params: {
    location: location

    lakeStorageConfiguration: lakeStorageConfiguration
    managedIdentityConfiguration: managedIdentityConfiguration
  }
}

module externalTables './resources/adx/tables.bicep' = {
  name: 'externalTables'
  params: {
    location: location
    storageUrl: lake.outputs.storageUrl
      
    adxClusterConfiguration: adxClusterConfiguration
    managedIdentityConfiguration: managedIdentityConfiguration
  }
}
