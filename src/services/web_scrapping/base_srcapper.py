import requests

from bs4 import BeautifulSoup
from typing import Optional, Set

from src.services.logger.logging import LoggerConfig

logger = LoggerConfig.set_up_logger()


class BaseScraper:
    def __init__(self, url: str):
        self.url = url

    def get_soup_content(self) -> BeautifulSoup:
        logger.info(f"Fetching content from URL: {self.url}")
        response = requests.get(self.url)
        response.raise_for_status()
        logger.info("Content fetched successfully, parsing HTML...")
        return BeautifulSoup(response.content, "html.parser")


class ArxivLinksScraper(BaseScraper):
    def __init__(self, url: str):
        super().__init__(url)
        self.links: Set[str] = set()

    def get_links(self) -> Set[str]:
        logger.info(f"Extracting links from {self.url}")
        soup = self.get_soup_content()
        h2_tags = soup.find_all("h2")

        for h2 in h2_tags[1:-1]:
            ul_tag = self._find_next_ul(h2)
            if ul_tag:
                for li in ul_tag.find_all("li"):
                    recent_link = li.find("a", string="recent")
                    if recent_link and "href" in recent_link.attrs:
                        full_url = f"{self.url}{recent_link['href']}"
                        self.links.add(full_url)
                        logger.info(f"Found recent link: {full_url}")
        logger.info(f"Total links extracted: {len(self.links)}")
        return self.links

    @staticmethod
    def _find_next_ul(tag) -> Optional[BeautifulSoup]:
        next_el = tag.find_next_sibling()
        while next_el and next_el.name != "ul":
            next_el = next_el.find_next_sibling()
        return next_el if next_el and next_el.name == "ul" else None




