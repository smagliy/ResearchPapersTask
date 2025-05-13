import asyncio
import aiohttp

from typing import List, Any

from src.services.s3.minio_service import BucketOperations
from src.config import BASE_URL, SSL_CONTEXT, HEADERS
from src.services.web_scrapping.base_srcapper import ArxivLinksScraper
from src.services.web_scrapping.asyncio_scrapper import AsyncArxivPageScraper
from src.services.logger.logging import LoggerConfig

logger = LoggerConfig.set_up_logger()


class ArxivScrapingManager:
    def __init__(self, minio_srv: BucketOperations, bucket: str):
        logger.info("Initializing ArxivScrapingManager...")
        self.urls = ArxivLinksScraper(BASE_URL).get_links()
        self.bucket_name = bucket
        self.minio = minio_srv

    @staticmethod
    def batched(iterable: List[Any], batch_size: int):
        for i in range(0, len(iterable), batch_size):
            yield iterable[i:i + batch_size]

    async def run_arxiv_papers(self, batch_size: int = 10, delay: int = 5):
        logger.info("Starting async scraping of arXiv papers.")
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=SSL_CONTEXT),
            headers=HEADERS
        ) as session:
            scraper = AsyncArxivPageScraper(session)
            logger.info("Fetching PDF links from collected URLs...")
            scrape_tasks = [scraper.get_papers_info(url) for url in self.urls]
            all_pdfs_nested = await asyncio.gather(*scrape_tasks)
            all_pdf_links = [pdf for sublist in all_pdfs_nested if sublist for pdf in sublist]
            for batch in self.batched(all_pdf_links, batch_size):
                logger.info(f"Processing batch with {len(batch)} PDFs.")
                upload_tasks = [
                    self.minio.upload_pdf_from_url(self.bucket_name, session, pdf_url)
                    for pdf_url in batch
                ]
                await asyncio.gather(*upload_tasks)
                logger.info(f"Batch uploaded. Waiting {delay} seconds before next batch.")
                await asyncio.sleep(delay)

