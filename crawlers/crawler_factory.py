"""
Crawler Factory - Dynamic crawler instantiation
"""
from typing import Dict, Any, Optional
from crawlers.base_crawler import BaseCrawler
from crawlers.local_seo_crawler import LocalSEOCrawler
from crawlers.general_seo_crawler import GeneralSEOCrawler
from crawlers.blogging_crawler import BloggingCrawler
from crawlers.ecommerce_crawler import EcommerceCrawler
from crawlers.news_media_crawler import NewsMediaCrawler
from crawlers.technical_seo_crawler import TechnicalSEOCrawler
from crawlers.competitor_crawler import CompetitorCrawler


CRAWLER_REGISTRY = {
    "local_seo": LocalSEOCrawler,
    "general_seo": GeneralSEOCrawler,
    "blogging": BloggingCrawler,
    "ecommerce": EcommerceCrawler,
    "news_media": NewsMediaCrawler,
    "technical_seo": TechnicalSEOCrawler,
    "competitor": CompetitorCrawler,
}


def create_crawler(crawler_type: str, config: Dict[str, Any], **kwargs) -> BaseCrawler:
    """
    Create a crawler instance by type.

    Args:
        crawler_type: Type of crawler to create
        config: Configuration dictionary
        **kwargs: Additional arguments to pass to crawler constructor

    Returns:
        Crawler instance

    Raises:
        ValueError: If crawler_type is not recognized
    """
    if crawler_type not in CRAWLER_REGISTRY:
        raise ValueError(
            f"Unknown crawler type: {crawler_type}. "
            f"Available types: {', '.join(CRAWLER_REGISTRY.keys())}"
        )

    crawler_class = CRAWLER_REGISTRY[crawler_type]
    return crawler_class(config, **kwargs)


def get_available_crawlers() -> list:
    """Get list of available crawler types."""
    return list(CRAWLER_REGISTRY.keys())
