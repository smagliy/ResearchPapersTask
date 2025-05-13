from io import BytesIO

from minio import Minio
from src.services.utils.decorators import handle_response
from src.services.logger.logging import LoggerConfig

logger = LoggerConfig.set_up_logger()


class BucketOperations(object):
    def __init__(self, minio_docker_url, minio_access_key, minio_secret_key):
        logger.info("Initializing a MinIO client...")
        self.client = Minio(minio_docker_url,
                            access_key=minio_access_key,
                            secret_key=minio_secret_key,
                            secure=False
                            )

    @handle_response
    async def upload_pdf_from_url(self, bucket: str, url: str,  content: bytes):
        file_name = url.split('/')[-1] + '.pdf'
        logger.info(f"Uploading PDF from URL: {url} to bucket '{bucket}' at '{file_name}'")
        self.write_content_to_file(bucket, file_name, content)
        logger.info(f"Uploaded: {file_name}")

    def read_from_bucket(self, bucket: str, path_to_file: str):
        try:
            logger.info(f"Reading file '{path_to_file}' from bucket '{bucket}'")
            data = self.client.get_object(bucket, path_to_file).read()
            logger.info(f"Successfully read file '{path_to_file}' from bucket '{bucket}'")
            return data
        except Exception as e:
            logger.error(f"Error reading file '{path_to_file}' from bucket '{bucket}': {e}")
            return None

    def write_content_to_file(self, bucket: str, file_name: str, content: bytes,
                              folder_path: str = "", content_type: str = 'application/pdf'):
        try:
            file_stream = BytesIO(content)
            self.client.put_object(
                bucket, folder_path+file_name,
                file_stream, length=len(content),
                content_type=content_type
            )
            logger.info(f"Successfully wrote file '{folder_path+file_name}' to bucket '{bucket}'")
        except Exception as e:
            logger.error(f"Error writing file '{file_name}' to bucket '{bucket}': {e}")
