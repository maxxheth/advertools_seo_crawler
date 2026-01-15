"""
Concurrent Manager - Manages multiple simultaneous crawler execution
"""
import asyncio
import threading
from typing import Dict, List, Any, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime


class ConcurrentCrawlerManager:
    """
    Manages concurrent execution of multiple crawlers.
    Handles resource allocation and result aggregation.
    """

    def __init__(self, max_concurrent: int = 3):
        """
        Initialize concurrent crawler manager.

        Args:
            max_concurrent: Maximum number of concurrent crawlers
        """
        self.max_concurrent = max_concurrent
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)
        self.active_crawlers = {}
        self.results = {}

    def run_crawler(self, crawler_id: str, crawler_instance: Any, start_urls: List[str]) -> str:
        """
        Submit crawler for execution.

        Args:
            crawler_id: Unique identifier for this crawler run
            crawler_instance: Crawler object with crawl() method
            start_urls: URLs to crawl

        Returns:
            Task ID for tracking
        """
        future = self.executor.submit(self._execute_crawler, crawler_id, crawler_instance, start_urls)
        self.active_crawlers[crawler_id] = {
            "future": future,
            "status": "running",
            "start_time": datetime.now(),
            "crawler_type": crawler_instance.crawler_type,
        }
        return crawler_id

    def run_multiple_crawlers(self, crawlers: Dict[str, tuple]) -> Dict[str, str]:
        """
        Run multiple crawlers concurrently.

        Args:
            crawlers: Dict mapping crawler_id to (crawler_instance, start_urls)

        Returns:
            Dict mapping crawler_id to task_id
        """
        task_ids = {}
        for crawler_id, (crawler_instance, start_urls) in crawlers.items():
            task_id = self.run_crawler(crawler_id, crawler_instance, start_urls)
            task_ids[crawler_id] = task_id
        return task_ids

    def _execute_crawler(self, crawler_id: str, crawler_instance: Any, start_urls: List[str]) -> Dict[str, Any]:
        """
        Execute a single crawler.

        Args:
            crawler_id: Crawler identifier
            crawler_instance: Crawler instance
            start_urls: URLs to crawl

        Returns:
            Crawl results
        """
        try:
            print(f"[{crawler_id}] Starting crawl...")
            
            # Run the crawler
            df = crawler_instance.crawl(start_urls)
            
            # Generate report if enabled
            report = crawler_instance.generate_report(include_analysis=True)
            
            result = {
                "crawler_id": crawler_id,
                "status": "success",
                "crawl_data": df,
                "report": report,
                "pages_crawled": len(df),
            }
            
            print(f"[{crawler_id}] Crawl complete ({len(df)} pages)")
            
        except Exception as e:
            result = {
                "crawler_id": crawler_id,
                "status": "error",
                "error": str(e),
            }
            print(f"[{crawler_id}] Error: {e}")

        self.results[crawler_id] = result
        self.active_crawlers[crawler_id]["status"] = result["status"]
        self.active_crawlers[crawler_id]["end_time"] = datetime.now()

        return result

    def get_status(self, crawler_id: str) -> Dict[str, Any]:
        """Get status of a specific crawler."""
        if crawler_id not in self.active_crawlers:
            return {"status": "unknown", "message": f"Crawler {crawler_id} not found"}

        crawler_info = self.active_crawlers[crawler_id]
        
        return {
            "crawler_id": crawler_id,
            "crawler_type": crawler_info.get("crawler_type"),
            "status": crawler_info.get("status"),
            "start_time": crawler_info.get("start_time").isoformat(),
            "end_time": crawler_info.get("end_time").isoformat() if crawler_info.get("end_time") else None,
            "duration": str(
                crawler_info.get("end_time") - crawler_info.get("start_time")
            ) if crawler_info.get("end_time") else "running",
        }

    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all crawlers."""
        return {
            crawler_id: self.get_status(crawler_id)
            for crawler_id in self.active_crawlers.keys()
        }

    def wait_for_completion(self, crawler_id: str = None) -> Dict[str, Any]:
        """
        Wait for crawler(s) to complete.

        Args:
            crawler_id: If specified, wait for specific crawler. Otherwise wait for all.

        Returns:
            Results of completed crawler(s)
        """
        if crawler_id:
            # Wait for specific crawler
            if crawler_id in self.active_crawlers:
                self.active_crawlers[crawler_id]["future"].result()
                return self.results.get(crawler_id)
        else:
            # Wait for all crawlers
            for future in as_completed([c["future"] for c in self.active_crawlers.values()]):
                future.result()

        return self.results

    def get_results(self, crawler_id: str = None) -> Dict[str, Any]:
        """Get results of completed crawler(s)."""
        if crawler_id:
            return self.results.get(crawler_id)
        return self.results

    def shutdown(self):
        """Shutdown the concurrent manager."""
        self.executor.shutdown(wait=True)
        print("Concurrent manager shutdown complete")
