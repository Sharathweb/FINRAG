import os
import shutil
import dotenv
import oss2
from oss2.credentials import EnvironmentVariableCredentialsProvider
from conf.config import STORAGE_DIR, STORAGE_TYPE
from utils.utils import logger

dotenv.load_dotenv()
endpoint = os.getenv("END_POINT")
bucket_name = os.getenv("BUCKET_NAME")

class Downloader:
    def __init__(self) -> None:
        # Initialize OSS bucket for cloud storage
        auth = oss2.ProviderAuth(EnvironmentVariableCredentialsProvider())
        self.bucket = oss2.Bucket(auth, endpoint, bucket_name)
        self.cache_dir = ".cache"
        
        # Ensure cache directory exists
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def get_file(self, remote_path: str, local_path: str = None):
        """Dispatches file download based on storage type."""
        if STORAGE_TYPE == 'local':
            return self._get_local_file(remote_path, local_path)
        else:
            return self._get_oss_file(remote_path, local_path)
        
    def _get_local_file(self, remote: str, local: str):
        """Copies file from local storage directory."""
        source = os.path.join(STORAGE_DIR, remote)
        shutil.copy(source, local)
        logger.info(f"File copied from {source} to {local}")
        
    def _get_oss_file(self, remote: str, local: str):
        """Downloads file from OSS with caching logic."""
        target_path = local or os.path.join(self.cache_dir, os.path.basename(remote))
        
        # Check cache before downloading
        if os.path.exists(target_path):
            logger.info(f"Cache hit: {target_path}")
            return target_path
            
        logger.info(f"Downloading {remote} from OSS to {target_path}...")
        self.bucket.get_object_to_file(remote, target_path)
        return target_path