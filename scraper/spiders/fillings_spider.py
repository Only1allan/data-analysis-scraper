from typing import Any
import scrapy
import os
from scrapy.http import Response
from urllib.parse import urljoin
from scrapy.utils.project import get_project_settings

from scraper.items import FilingItem
from scraper.storage.checkpoint_manager import CheckpointManager

class FilingsSpider(scrapy.Spider):
    """Spider to scrape 13F filings for managers."""

    name = "filings"
    custom_settings = get_project_settings()
    base_url = os.getenv("BASE_URL", "https://13f.info")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.checkpoint = CheckpointManager(self.custom_settings.get('CHECKPOINT_PATH'))
        self.max_filings = self.custom_settings.getint('MAX_FILINGS_PER_MANAGER', 2)

    async def start(self):
        """
        Generate start requests from checkpoint or command line arguments.
        This allows the spider to be run independently or as part of a chain.
        """
        for manager_id, data in self.checkpoint.data.items():
            if not data.get("filings"):
                yield scrapy.Request(
                    url=f"{self.custom_settings.get('BASE_URL')}{data['filing_url']}",
                    meta={"manager_id": manager_id, "manager_name": data["name"]}
                )

    async def parse(self, response: Response):
        """Parse the filings page for a manager."""
        manager_id = response.meta.get("manager_id")
        manager_name = response.meta.get("manager_name")

        filings = response.css("#managerFilings tbody tr")

        if not filings:
            self.logger.warning(f"No filings found for manager {manager_name}")
            return

        filings_count = 0
        for filing in filings:
            cells = filing.css("td")

            if len(cells) < 7:
                continue

            form_type = cells[4].css("::text").get("").strip()

            if form_type != "13F-HR":
                continue

            quarter_link = cells[0].css("a")
            quarter = quarter_link.css("::text").get("").strip()
            filing_url = quarter_link.attrib.get("href", "")
            
            absolute_filing_url = urljoin(self.base_url, filing_url)
            filing_id = cells[6].css("::text").get("").strip()
            filing_item = FilingItem(
                manager_id=manager_id,
                manager_name=manager_name,
                quarter=quarter,
                filing_url=filing_url,
                holdings=cells[1].css("::text").get("").strip(),
                value=cells[2].css("::text").get("").strip(),
                top_holdings=cells[3].css("::text").get("").strip(),
                form_type=form_type,
                filing_date=cells[5].css("::text").get("").strip(),
                filing_id=filing_id
            )

            yield filing_item

            if filings_count < self.max_filings and filing_url:
                yield scrapy.Request(
                    url=absolute_filing_url,
                    callback=self.parse_holdings,
                    meta={
                        "manager_id": manager_id,
                        "manager_name": manager_name,
                        "quarter": quarter,
                        "filing_date": filing_item["filing_date"],
                        "filing_id": filing_id
                    },
                )

            filings_count += 1
            if filings_count >= self.max_filings:
                break

        self.logger.info(f"Processed {filings_count} filings for manager {manager_name}")