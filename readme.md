# Using Azure Cognitive and AI Services to Dub Video Translations

## Deployment Steps:
Local Setup:
1. Clone this repository to your local machine for local development.
1. Follow TODO: this guide to set up your local machine to develop Logic Apps locally.
1. Follow TODO: this guide to set up your local machine to develop Azure Functions with python. 
Azure Resources:
1. Create an Azure app registration (a.k.a. service principal). This will be used to authenticate to various services. 
    * the service principal needs access to these resources TODO
1. Create a new resource group in Azure
1. Deploy an Azure Storage Account w/ hierarchichal namespace enabled (a.k.a Azure Data Lake Storage Gen 2 or ADLS gen 2)
    * Locally redundant for pilot/POC work
    * HNS enabled
    * after deployment create a file system called "videodubbing"
1. Deploy an Azure Logic App
    * Publish: Workflow
    * Plan type: Standard
    * App Service Plan: Create New
    * Plan Sku and Size: WS1
    * Create new storage account for workflow state and run history.
    * Enable application insights (create a new instance)
1.  Deploy Video Analyzer
    * Create a media services account
    * Create a media services storage account
    * Create a user-assignmed managed identity
    * Check "I have all the rights to use the content/file, and agree that it will be handled per the Online Services Terms and the Microsoft Privacy Statement." 
    * After deployment, go to https://api-portal.videoindexer.ai/products, sign in, and then click on Authorization. Create a new subscription name. 
1. Deploy Speech API
    * Defaults are okay.
1. Deploy an Azure Key Vault
    * Pricing tier: Standard
    * Add a Access policy with all key permissions using the app registration you created previously. 
    * After deployment, create the following secrets and apply their 

    Secret Name |Description | Example Value
    ---|---|---
    TENANT-ID | The Azure Active Directory tenant ID where you created the app registration and deployed your resources. | "00000000-0000-0000-0000-000000000000"
    CLIENT-APP-ID | Application ID of the service principal you created | "00000000-0000-0000-0000-000000000000"
    CLIENT-APP-SECRET | Secret key of the service prinicpal | 
    AVAM-ACCOUNT-ID | Guid you can in the Azure portal or at videoindexer.ai | "00000000-0000-0000-0000-000000000000"
    AVAM-ACCOUNT-REGION | Azure region where AVAM was deployed | i.e. eastus2, westus2, etc.     
    AVAM-RESOURCE-ID | Found in the Azure portal in the AVAM resource, under the "Properties" tab | Ex. "/subscriptions/{your_subscription_id_guid}/<br/>resourceGroups/{resource_group_name}/providers/<br/>Microsoft.VideoIndexer/accounts/{avam_account_name}"
    AVAM-API-KEY | Created at https://api-portal.videoindexer.ai/product and accessed at https://api-portal.videoindexer.ai/profile |
    SPEECH-LANGUAGES-CONFIG | A json array of the various languages that you want to translate and dub the languages to. You can find [supported languages for AVAM](https://api-portal.videoindexer.ai/api-details#api=Operations&operation=Get-Video-Captions) here and [supported voices for Azure Speech API](https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support?tabs=speechtotext#prebuilt-neural-voices) | See below

Sample speech languages config:
```json [
  {
    "language-text-code": "zh-Hans",
    "language-voice-code": "zh-CN",
    "language-voice-name": "zh-CN-XiaomoNeural",
    "language-display-name": "Chinese"
  },
  {
    "language-text-code": "es-MX",
    "language-voice-code": "es-MX",
    "language-voice-name": "es-MX-JorgeNeural",
    "language-display-name": "Spanish (Mexico)"
  },
  ...etc...
]
```

## Logic App Flows: 
0. **GetAVAMAccessToken:** used by the other workflows. Gets an Azure AD management access token that is used to interact with Azure Video Analyzer for Media. 
0. **UploadVideoToAVAM:** triggered by video upload to Azure Storage. Generates a SAS URI and then passes it in the request to AVAM to begin processing the video. 
