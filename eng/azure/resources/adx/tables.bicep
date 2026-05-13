
param storageUrl string

param adxClusterName string
param adxDatabaseName string

param forceUpdateTag string = utcNow()

var content = concat(
  loadTextContent('./create-telemetry-harvesting-stem.kql')
)

var scriptContent = replace(
  content,
  '__STORAGE_URL__',
  storageUrl
)

resource externalTableScript 'Microsoft.Kusto/clusters/databases/scripts@2023-08-15' = {
  name: '${adxClusterName}/${adxDatabaseName}/externalTables'

  properties: {
    #disable-next-line use-secure-value-for-secure-inputs
    scriptContent: scriptContent
    continueOnErrors: false
    forceUpdateTag: forceUpdateTag
  }
}
