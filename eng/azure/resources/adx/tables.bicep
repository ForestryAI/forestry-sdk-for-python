
param location string
param storageUrl string

param adxClusterConfiguration object
param managedIdentityConfiguration object

param forceUpdateTag string = utcNow()


resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: managedIdentityConfiguration.name
  location: location
}

#disable-next-line prefer-interpolation
var content = concat(
  loadTextContent('./create-telemetry-harvesting-stem.kql'),
  '\n\n',
  loadTextContent('./create-telemetry-harvesting-log.kql')
)

var contentWithStorageUrl = replace(
  content,
  '__STORAGE_URL__',
  storageUrl
)

var contentWithManagedClientId = replace(
  contentWithStorageUrl,
  '__UAMI_OBJECT_ID__',
  managedIdentity.properties.principalId
)

resource externalTableScript 'Microsoft.Kusto/clusters/databases/scripts@2023-08-15' = {
  name: '${adxClusterConfiguration.name}/${adxClusterConfiguration.databaseName}/externalTables'

  properties: {
    #disable-next-line use-secure-value-for-secure-inputs
    scriptContent: contentWithManagedClientId
    continueOnErrors: false
    forceUpdateTag: forceUpdateTag
  }
}
