import logging
from typing import Dict, List, Any
from scrapy.exceptions import DropItem
from .storage.checkpoint_manager import CheckpointManager
from scraper.items import ManagerItem, FilingItem, HoldingItem


class CheckpointPipeline:
    """Pipeline for saving items to checkpoint."""

    def __init__(self, checkpoint_path):
        self.checkpoint_path = checkpoint_path
        self.checkpoint = CheckpointManager(checkpoint_path)
        self.logger = logging.getLogger(__name__)
        self.stock_quarters: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            checkpoint_path=crawler.settings.get('CHECKPOINT_PATH', 'checkpoints/13f-info.json')
        )

    def process_item(self, item, spider):
        try:
            if isinstance(item, ManagerItem):
                manager_id = item['id']
                if manager_id in self.checkpoint:
                    self.logger.info(f"Skipping already processed manager: {item['name']}")
                    raise DropItem(f"Manager {manager_id} already processed")

                self.checkpoint[manager_id] = {
                    'id': manager_id,
                    'name': item['name'],
                    'filing_url': item['link'],
                    'filings': {}
                }

            elif isinstance(item, FilingItem):
                manager_id = item["manager_id"]
                filing_id = item["filing_id"]


                if manager_id in self.checkpoint:
                    self.checkpoint[manager_id]["filings"][filing_id] = {
                        "quarter": item["quarter"],
                        "filing_url": item["filing_url"],
                        'filing_date': item['filing_date'],
                        'filing_id': item['filing_id'],
                        "holdings": {}
                    }
            elif isinstance(item, HoldingItem):
                manager_id = item["manager_id"]
                filing_id = item["filing_id"]
                holding_id = item["symbol"]

                if manager_id in self.checkpoint and filing_id in self.checkpoint[manager_id]["filings"]:
                    self.checkpoint[manager_id]["filings"][filing_id]["holdings"][holding_id] = {
                        "shares": item["shares"],
                        "value": item["value"]
                    }
            return item
        except Exception as e:
            self.logger.error(f"Error in checkpoint pipeline: {e}")
            return item

    def close_spider(self, spider):
        """Save final checkpoint when spider closes."""
        self.checkpoint.save()
        self.logger.info(f"Checkpoint saved to {self.checkpoint_path}")
