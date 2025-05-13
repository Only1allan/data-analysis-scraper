import json
import scrapy
from scrapy.http import Response
from scrapy.utils.project import get_project_settings
from scraper.items import HoldingItem
from scraper.storage.checkpoint_manager import CheckpointManager

class HoldingsSpider(scrapy.Spider):
    """Spider to scrape holdings from 13F filings."""

    name = "holdings"
    custom_settings = get_project_settings()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.checkpoint = CheckpointManager(self.custom_settings.get('CHECKPOINT_PATH'))
        self.base_holdings_url = self.custom_settings.get("HOLDING_LIST_BASE_URL")

    async def start(self):
        """
        Generate start requests from checkpoint.
        This allows the spider to be run independently.
        """
        for manager_id, data in self.checkpoint.data.items():
            for filing_id, filing in data["filings"].items():
                yield scrapy.Request(
                    url=f"{self.custom_settings.get('BASE_URL')}/data/13f/{filing_id}",
                    meta={"manager_id": manager_id, "filing_id": filing_id, "quarter": filing["quarter"],
                          "filing_date": filing["filing_date"]}
                )


    async def parse(self, response: Response):
        """Parse the holdings page for a filing."""
        manager_id = response.meta.get("manager_id")
        manager_name = response.meta.get("manager_name")
        quarter = response.meta.get("quarter", "")
        filing_date = response.meta.get("filing_date", "")
        filing_id = response.meta.get("filing_id", "")

        self.logger.info(f"Processing holdings for {manager_id}, quarter {quarter}")
        response_json = json.loads(response.text)


        holdings = response_json["data"]

        for holding in holdings:
            holding_item = HoldingItem(
                manager_id=manager_id,
                manager_name=manager_name,
                filing_date=filing_date,
                quarter=quarter,
                symbol=holding[0],
                issuer=holding[1],
                cl=holding[2],
                cusip=holding[3],
                value=holding[4],
                percentage=holding[5],
                shares=holding[6],
                principal=holding[7],
                option=holding[8],
                filing_id=filing_id
            )

            yield holding_item

        self.logger.info(f"Processed {len(holdings)} holdings for {manager_name}, quarter {quarter}")