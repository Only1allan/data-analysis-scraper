#!/usr/bin/env python
"""
Main entry point for the 13F filings scraper.
This script orchestrates the execution of all spiders in the correct order.
"""
import argparse
import asyncio
import logging
import sys
import platform

# Ensure the right asyncio policy on Windows
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# 🛠️ Install the correct Twisted reactor BEFORE importing `reactor` or `task`
from twisted.internet import asyncioreactor
asyncioreactor.install()  # MUST happen before any other twisted import

# Now it's safe to import the reactor
from twisted.internet import defer, reactor, task

# Now continue with your other imports
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from dotenv import load_dotenv

from .spiders.managers_spider import ManagersSpider
from .spiders.fillings_spider import FilingsSpider
from .spiders.holdings_spider import HoldingsSpider
from .storage.checkpoint_manager import CheckpointManager
from .storage.processor import process_data



def setup_logging(log_level='INFO'):
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('13f_scraper.log')
        ]
    )



def main():


    """Main entry point."""
    # Load environment variables
    load_dotenv()

    # Set up logging
    logger = logging.getLogger(__name__)

    # Update settings
    settings = get_project_settings()


    runner = CrawlerRunner(settings)
    @defer.inlineCallbacks
    def crawl(__reactor):
        yield runner.crawl(ManagersSpider)
        yield runner.crawl(FilingsSpider)
        yield runner.crawl(HoldingsSpider)

        checkpoint = CheckpointManager(settings.get("CHECKPOINT_PATH"))
        process_data(checkpoint.get_all(), settings.get("OUTPUT_PATH"))
        reactor.stop()


    logger.info("Starting crawl process...")
    task.react(crawl)


if __name__ == "__main__":
    main()