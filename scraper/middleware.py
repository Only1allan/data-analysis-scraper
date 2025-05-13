"""
Scrapy middlewares for the 13F scraper project.
"""

import logging
import random
from typing import Union, Optional
from scrapy import signals
from scrapy.http import Response, Request
from scrapy.spiders import Spider
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message

logger = logging.getLogger(__name__)


class RandomUserAgentMiddleware:
    """Middleware to rotate user agents."""

    def __init__(self):
        self.user_agents = [
            # Chrome
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
            # Firefox
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
            # Safari
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            # Edge
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59'
        ]

    def process_request(self, request: Request, spider: Spider) -> None:
        """Select a random user agent for the request."""
        user_agent = random.choice(self.user_agents)
        request.headers['User-Agent'] = user_agent


class CustomRetryMiddleware(RetryMiddleware):
    """Custom retry middleware with improved logging."""

    def process_response(self, request: Request, response: Response, spider: Spider) -> Union[Response, Request]:
        """Process response and retry if needed."""
        if request.meta.get('dont_retry', False):
            return response

        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            logger.warning(f"Retrying {request.url} (failed with {response.status}): {reason}")
            return self._retry(request, reason, spider) or response

        return response

    def process_exception(self, request: Request, exception: Exception, spider: Spider) -> Optional[Request]:
        """Process exception and retry if needed."""
        logger.error(f"Error processing {request.url}: {exception.__class__.__name__}: {str(exception)}")
        return super().process_exception(request, exception, spider)


class SpiderErrorMiddleware:
    """Middleware to handle spider errors."""

    @classmethod
    def from_crawler(cls, crawler):
        """Connect to signals."""
        middleware = cls()
        crawler.signals.connect(middleware.spider_error, signal=signals.spider_error)
        return middleware

    def spider_error(self, failure, response, spider):
        """Handle spider errors."""
        logger.error(f"Spider error processing {response.url}: {failure.value}")