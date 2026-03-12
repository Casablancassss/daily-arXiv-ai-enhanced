# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import arxiv
import json
import os
import sys
import time
import logging
from datetime import datetime, timedelta


class DailyArxivPipeline:
    """Pipeline for processing arXiv papers with rate limiting and error handling."""

    def __init__(self):
        self.page_size = 100
        self.client = arxiv.Client(self.page_size)
        self.last_request_time = 0
        self.logger = logging.getLogger(__name__)
        # Rate limit configurable via environment variable
        self.rate_limit = int(os.environ.get("ARXIV_RATE_LIMIT", "5"))

    def process_item(self, item: dict, spider):
        """Process a single paper item with rate limiting and error handling."""
        try:
            # Rate limiting: add delay between requests to avoid HTTP 429
            current_time = time.time()
            elapsed = current_time - self.last_request_time
            if elapsed < self.rate_limit:
                time.sleep(self.rate_limit - elapsed)
            self.last_request_time = time.time()

            # Get paper ID safely
            paper_id = item.get('id')
            if not paper_id:
                self.logger.warning("Item missing 'id' field, skipping")
                return item

            item["pdf"] = f"https://arxiv.org/pdf/{paper_id}"
            item["abs"] = f"https://arxiv.org/abs/{paper_id}"

            # Search for paper details
            search = arxiv.Search(id_list=[paper_id])

            # Safely get results with exception handling
            try:
                results = list(self.client.results(search))
                if not results:
                    self.logger.warning(f"No results found for paper {paper_id}")
                    return item

                paper = results[0]
            except StopIteration:
                self.logger.warning(f"No results found for paper {paper_id}")
                return item
            except Exception as e:
                self.logger.error(f"Error fetching paper {paper_id}: {e}")
                return item

            # Extract paper details safely
            item["authors"] = [a.name for a in paper.authors] if paper.authors else []
            item["title"] = paper.title or "Untitled"
            item["categories"] = paper.categories or []
            item["comment"] = paper.comment or ""
            item["summary"] = paper.summary or ""

            return item

        except KeyError as e:
            self.logger.error(f"Missing required field in item: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error processing item: {e}")
            raise
