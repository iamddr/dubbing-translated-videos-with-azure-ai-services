from http import client
import logging
import os
import random
import json
import time
import azure.functions as func
from azure.identity import ClientSecretCredential
from azure.mgmt.media import AzureMediaServices
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.mgmt.media.models import (
    Asset,
    Job,
    JobInputAsset,
    JobOutputAsset,
)


def main(req: func.HttpRequest) -> func.HttpResponse:

    ## Get the video_id from the request
    req_body = req.get_json()
    video_id = req_body.get("video_id")

    ## Get the blob sas URI included in the request
    blob_sas_uri = req_body.get("blob_sas_uri")

    ## Get the target audio file details
    audio_blob = BlobClient.from_blob_url(blob_sas_uri)
    audio_blob_name = audio_blob.blob_name.split("/")[-1]

    ## Unique identifier for this job
    uniqueness = random.randint(0,9999)

    ## authenticate to the stuff
    client_cred = ClientSecretCredential(
        client_id=os.environ["CLIENT_APP_ID"],
        client_secret=os.environ["CLIENT_APP_SECRET"],
        tenant_id=os.environ["CLIENT_APP_TENANT_ID"],
    )

    media_client = AzureMediaServices(
        credential=client_cred, subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"]
    )

    ## with the video analyzer/indexer video id, look up the streaming locators
    locators = media_client.streaming_locators.list(
        account_name=os.environ["MEDIA_SERVICES_ACCOUNT_NAME"],
        resource_group_name=os.environ["MEDIA_SERVICES_RESOURCE_GROUP"],
    )
    locators_list = []
    for i, r in enumerate(locators):
        locators_list.append(r.as_dict())

    ## get the properties.assetname for the streaming locator that starts with the video id
    video_asset_name = [
        locator["asset_name"]
        for locator in locators_list
        if locator["name"].startswith(video_id)
    ][0]

    ## get the container name from asset details using the asset name
    video_asset = media_client.assets.get(
        resource_group_name=os.environ["MEDIA_SERVICES_RESOURCE_GROUP"],
        account_name=os.environ["MEDIA_SERVICES_ACCOUNT_NAME"],
        asset_name=video_asset_name,
    )
    video_asset_id = video_asset.as_dict()["asset_id"]
    video_container_name = video_asset.as_dict()["container"]

    ## create an asset and container for the audio file and upload the audio file
    audio_input_asset = media_client.assets.create_or_update(
        resource_group_name=os.environ["MEDIA_SERVICES_RESOURCE_GROUP"],
        account_name=os.environ["MEDIA_SERVICES_ACCOUNT_NAME"],
        parameters=Asset(),
        asset_name=audio_blob_name,
    )

    audio_input_container = "asset-" + audio_input_asset.asset_id
    blob_service_client = BlobServiceClient.from_connection_string(
        os.environ["MEDIA_SERVICES_STORAGE_ACCOUNT_CONNECTION_STRING"]
    )

    audio_input_container_client = blob_service_client.get_container_client(
        audio_input_container
    )
    if not audio_input_container_client.exists():
        audio_input_container_client = audio_input_container_client.create_container(
            audio_input_container
        )

    audio_input_blob_client = blob_service_client.get_blob_client(
        container=audio_input_container, blob=audio_blob_name
    )

    audio_input_blob_client.upload_blob_from_url(blob_sas_uri, overwrite=True)

    # create a media services job to encode the audio, output directly to the container (if possible)
    video_output_asset = media_client.assets.get(
        resource_group_name=os.environ["MEDIA_SERVICES_RESOURCE_GROUP"],
        account_name=os.environ["MEDIA_SERVICES_ACCOUNT_NAME"],
        asset_name=video_asset_name,
    )

    job_name = "job-" + video_id + f"-{audio_blob_name}-encode-{str(uniqueness)}"

    job_input = JobInputAsset(asset_name=audio_blob_name)
    job_output = JobOutputAsset(asset_name=video_asset_name)

    theJob = Job(input=job_input, outputs=[job_output])

    current_job = media_client.jobs.create(
        account_name=os.environ["MEDIA_SERVICES_ACCOUNT_NAME"],
        resource_group_name=os.environ["MEDIA_SERVICES_RESOURCE_GROUP"],
        job_name=job_name,
        parameters=theJob,
        transform_name="MP3toAACMP4"
    )

    return func.HttpResponse(
        f"The job ended with the status: {json.dumps(current_job.as_dict(), indent=4)}", 
        status_code=200
    )