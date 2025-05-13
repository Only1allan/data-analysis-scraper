import string
from typing import Any
from urllib.parse import urlparse
import scrapy
from scrapy.http import Response
from scrapy.utils.project import get_project_settings
from scraper.items import ManagerItem
from scraper.storage.checkpoint_manager import CheckpointManager


class ManagersSpider(scrapy.Spider):
    """Spider to scrape fund managers."""

    name = "managers"
    custom_settings = get_project_settings()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.checkpoint = CheckpointManager(self.custom_settings.get('CHECKPOINT_PATH'))
        self.processed_managers = set(self.checkpoint.data.keys())

    async def start(self):
        """Generate start requests for each alphabet page."""
        base_url = self.custom_settings.get('MANAGER_LIST_BASE_URL')
        pages = list(string.ascii_lowercase) + ['0']

        for page in pages:
            url = f"{base_url}/{page}"
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={"page": page},
                errback=self.handle_error
            )


    async def parse(self, response: Response) -> Any:
        """Parse the manager list page."""
        page = response.meta.get("page", "")
        self.logger.info(f"Processing managers page: {page}")
        manager_links = response.css("table a[href*='/manager/']")

        managers_count = 0
        for link in manager_links:
            href = link.attrib["href"]
            name = link.css("::text").get("").strip()
            parsed = urlparse(href)
            path_parts = parsed.path.strip('/').split('/')

            if len(path_parts) < 2:
                continue

            manager_id = path_parts[-1].split('-')[0]

            if manager_id in self.processed_managers:
                self.logger.debug(f"Skipping already processed manager: {name}")
                continue

            managers_count += 1

            yield ManagerItem(
                id=manager_id,
                name=name,
                link=href
            )

        self.logger.info(f"Found {managers_count} new managers on page {page}")

    async def handle_error(self, failure):
        """Handle request errors."""
        self.logger.error(f"Request failed: {failure.value}")