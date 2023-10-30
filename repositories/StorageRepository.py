import os
import uuid
from urllib.parse import urlparse, unquote

from google.cloud import storage
import tempfile


class StorageRepository:
    def __init__(self, bucket_name):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(os.environ["GOOGLE_APP_CRED"])
            credentials_path = temp_file.name
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

        self.bucket_name = bucket_name
        self.storage_client = storage.Client()
        os.remove(credentials_path)

    def get_bucket(self):
        return self.storage_client.get_bucket(self.bucket_name)

    def create_folder(self, folder_path):
        """Create a folder in GCS by creating a zero-byte object."""
        blob_name = folder_path if folder_path.endswith('/') else folder_path + '/'
        bucket = self.get_bucket()
        blob = bucket.blob(blob_name)
        blob.upload_from_string('')

    def upload_blob(self, data, blob_name):
        filename = f"{uuid.uuid4()}.tmp"
        with open(filename, "wb") as f:
            f.write(data)
        bucket = self.get_bucket()
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(filename)
        os.remove(filename)
        return blob.public_url

    def upload_file(self, file_path, blob_name):
        bucket = self.get_bucket()
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(file_path)
        return blob.public_url

    def delete_file(self, blob_url):
        blob_name = self.get_blob_name(blob_url)
        try:
            bucket = self.get_bucket()
            blob = bucket.blob(blob_name)
            blob.delete()
            return True
        except Exception as e:
            print(f"Error while deleting blob with URL {blob_url}: {e}")
            return False

    def get_blob_name(self, blob_url):
        # Parse the URL to extract the blob name
        parsed_url = urlparse(blob_url)
        blob_name = unquote(parsed_url.path[1:])
        blob_name = blob_name.replace(f'{self.bucket_name}/', '', 1)
        return blob_name

    def get_public_url(self, blob_name):
        bucket = self.get_bucket()
        blob = bucket.blob(blob_name)
        return blob.public_url

    def download_blob_by_name(self, blob_name):
        bucket = self.get_bucket()
        blob = bucket.blob(blob_name)
        return blob.download_as_bytes()

    def download_blob_by_url(self, blob_url):
        blob_name = self.get_blob_name(blob_url)
        bucket = self.get_bucket()
        blob = bucket.blob(blob_name)
        return blob.download_as_bytes()



