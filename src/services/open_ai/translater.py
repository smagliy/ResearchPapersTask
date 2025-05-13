from openai import OpenAI
from io import BytesIO

from src.services.s3.minio_service import BucketOperations
from src.services.utils.file_handler import PDFHandler
from src.config import API_KEY
from src.services.logger.logging import LoggerConfig

logger = LoggerConfig.set_up_logger()


class OpenAITranslater:
    def __init__(
        self,
        minio_client: BucketOperations,
        bucket_name: str,
        pdf_file_name: str,
        language: str = 'ukrainian'
    ):
        self.client = OpenAI(api_key=API_KEY)
        self.minio = minio_client
        self.bucket = bucket_name
        self.pdf_file_name = pdf_file_name
        self.language = language
        logger.info(f"Initialized OpenAITranslater for file '{pdf_file_name}' to language '{language}'.")

    def _download_pdf(self) -> BytesIO:
        logger.info(f"Downloading PDF '{self.pdf_file_name}' from bucket '{self.bucket}'...")
        response = self.minio.read_from_bucket(self.bucket, self.pdf_file_name)
        return BytesIO(response)

    def _translate_text(self, text: str) -> str:
        logger.info(f"Sending text for translation to '{self.language}'...")
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"Please translate the following text to {self.language}:\n\n{text}"}
            ]
        )
        return response.choices[0].message.content.strip()

    def translate_pdf_file(self) -> str:
        pdf_stream = self._download_pdf()
        all_text = PDFHandler.extract_text_from(pdf_stream)
        logger.info("Text extraction complete.")
        translated_text = self._translate_text(all_text)
        logger.info("Translation process complete.")
        return translated_text


