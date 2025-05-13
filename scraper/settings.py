import os
from dotenv import load_dotenv

load_dotenv()

BOT_NAME = "scraper"

SPIDER_MODULES = ["scraper.spiders"]
NEWSPIDER_MODULE = "scraper.spiders"

# Crawl responsibly by identifying yourself on the user agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = int(os.getenv("CONCURRENT_REQUESTS", "100"))
CONCURRENT_REQUESTS_PER_DOMAIN = int(os.getenv("CONCURRENT_REQUESTS_PER_DOMAIN", "15"))

# Disable download delay (use with caution to avoid bans)
DOWNLOAD_DELAY = 0
RANDOMIZE_DOWNLOAD_DELAY = False

REACTOR_THREADPOOL_MAXSIZE = 15

# Enable built-in cache
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600
HTTPCACHE_DIR = "httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = [503, 504, 400, 401, 403, 404, 408]

# Retry configuration
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Timeout configuration
DOWNLOAD_TIMEOUT = 30

# Log level
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Configure item pipelines
ITEM_PIPELINES = {
   "scraper.pipelines.CheckpointPipeline": 300,
}

# Base URLs
BASE_URL = os.getenv("BASE_URL", "https://13f.info")
MANAGER_LIST_BASE_URL = os.getenv("MANAGER_LIST_BASE_URL", f"{BASE_URL}/managers")
HOLDING_LIST_BASE_URL = os.getenv("HOLDING_LIST_BASE_URL", f"{BASE_URL}/data")

# Checkpoint file path
CHECKPOINT_PATH = os.getenv("CHECKPOINT_PATH", "checkpoints/13f-info.json")

# Output file path
OUTPUT_PATH = os.getenv("OUTPUT_PATH", "data/processed_data.csv")

# Number of most recent filings to process
MAX_FILINGS_PER_MANAGER = int(os.getenv("MAX_FILINGS_PER_MANAGER", "2"))