import os
from urllib.parse import urlparse

from google.cloud import storage
import tempfile
import json


class StorageRepository:
    def __init__(self, bucket_name):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(os.environ["GOOGLE_APP_CRED"])
            credentials_path = temp_file.name
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

        self.bucket_name = bucket_name
        self.storage_client = storage.Client()

    def get_bucket(self):
        return self.storage_client.get_bucket(self.bucket_name)

    def upload_file(self, file_path, blob_name):
        bucket = self.get_bucket()
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(file_path)
        return blob.public_url

    def get_public_url(self, blob_name):
        bucket = self.get_bucket()
        blob = bucket.blob(blob_name)
        return blob.public_url

    def download_blob(self, blob_name):
        bucket = self.get_bucket()
        blob = bucket.blob(blob_name)
        return blob.download_as_bytes()

