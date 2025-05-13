import aiohttp

from bs4 import BeautifulSoup
from typing import Optional, Set

from src.services.logger.logging import LoggerConfig

logger = LoggerConfig.set_up_logger()


class AsyncBaseScraper:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def get_soup_content(self, url: str) -> Optional[BeautifulSoup]:
        logger.info(f"Fetching async content from URL: {url}")
        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                text = await response.text()
                logger.info(f"Successfully fetched and parsed content from: {url}")
                return BeautifulSoup(text, "html.parser")
        except aiohttp.ClientError as e:
            logger.error(f"Request failed for URL: {url} -> {e}")
            return None


class AsyncArxivPageScraper(AsyncBaseScraper):
    async def get_papers_info(self, url: str, limit: int = 5) -> Optional[Set[str]]:
        logger.info(f"Extracting paper info from {url} with limit={limit}")
        soup = await self.get_soup_content(url)
        if not soup:
            logger.warning(f"Failed to retrieve or parse content from: {url}")
            return None
        pdf_links_articles = set()
        for dt, dd in zip(soup.find_all("dt"), soup.find_all("dd")):
            pdf_link = self._make_full_link(dt.find("a", title="Download PDF"))
            if pdf_link and pdf_link not in pdf_links_articles:
                pdf_links_articles.add(pdf_link)
                logger.info(f"Found PDF link: {pdf_link}")
            if len(pdf_links_articles) >= limit:
                logger.info(f"Limit of {limit} PDF links reached.")
                break
        return pdf_links_articles

    @staticmethod
    def _make_full_link(tag) -> Optional[str]:
        return f"https://arxiv.org{tag['href']}" if tag and 'href' in tag.attrs else None

