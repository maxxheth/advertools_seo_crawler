"""
Specialized SEO Crawler Classes
"""
from crawlers.base_crawler import BaseCrawler
from crawlers.local_seo_crawler import LocalSEOCrawler
from crawlers.general_seo_crawler import GeneralSEOCrawler
from crawlers.blogging_crawler import BloggingCrawler
from crawlers.ecommerce_crawler import EcommerceCrawler
from crawlers.news_media_crawler import NewsMediaCrawler
from crawlers.technical_seo_crawler import TechnicalSEOCrawler
from crawlers.competitor_crawler import CompetitorCrawler

__all__ = [
    "BaseCrawler",
    "LocalSEOCrawler",
    "GeneralSEOCrawler",
    "BloggingCrawler",
    "EcommerceCrawler",
    "NewsMediaCrawler",
    "TechnicalSEOCrawler",
    "CompetitorCrawler",
]
