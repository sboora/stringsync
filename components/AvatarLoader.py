import os

from repositories.StorageRepository import StorageRepository
from repositories.UserRepository import UserRepository


class AvatarLoader:
    def __init__(self, storage_repo: StorageRepository,
                 user_repo: UserRepository):
        self.storage_repo = storage_repo
        self.user_repo = user_repo

    def get_avatar(self, avatar_name):
        # Directory where avatars are stored locally
        local_avatars_directory = 'avatars'

        # Construct the local file path for the badge
        local_file_path = os.path.join(local_avatars_directory, f"{avatar_name}.png")

        # Check if the avatar exists locally
        if os.path.exists(local_file_path):
            return local_file_path

        # If avatar not found locally, attempt to download from remote
        remote_path = f"{self.get_avatars_bucket()}/{avatar_name}.png"
        success = self.storage_repo.download_blob_and_save(remote_path, local_file_path)

        if success:
            return local_file_path
        else:
            print(f"Failed to download avatar named '{avatar_name}' from remote location.")
            return None

    def cache_avatars(self):
        # Directory where badges are stored locally
        local_avatars_directory = self.get_avatars_bucket()

        # Ensure the directory exists
        if not os.path.exists(local_avatars_directory):
            os.makedirs(local_avatars_directory)

        avatars = self.user_repo.get_all_avatars()
        # Check and download avatars
        for avatar in avatars:
            self._download_avatar_if_not_exists(avatar['name'], local_avatars_directory)

    def _download_avatar_if_not_exists(self, avatar_name, local_avatars_directory):
        # Construct the local file path
        local_file_path = os.path.join(local_avatars_directory, f"{avatar_name}.png")

        # Check if the badge exists locally
        if not os.path.exists(local_file_path):
            # If the badge doesn't exist locally, download it
            remote_badge_path = f"{self.get_avatars_bucket()}/{avatar_name}.png"
            self.storage_repo.download_blob_and_save(remote_badge_path, local_file_path)

    @staticmethod
    def get_avatars_bucket():
        return 'avatars'

