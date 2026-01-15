#!/usr/bin/env python3
"""
Advertools SEO Crawler - Main Entry Point
Advanced web crawling and analysis system with specialized crawlers for different use cases.
"""
import os
import sys
from utils.config_loader import load_config
from crawlers.crawler_factory import create_crawler, get_available_crawlers
from utils.concurrent_manager import ConcurrentCrawlerManager
from utils.websocket_server import WebSocketManager


def load_config_wrapper():
    """Load configuration from YAML and environment variables."""
    return load_config()


def list_available_crawlers():
    """Print list of available crawler types."""
    crawlers = get_available_crawlers()
    print("\nAvailable Crawler Types:")
    print("-" * 60)
    
    descriptions = {
        'local_seo': 'Local SEO - NAP consistency, LocalBusiness schema, Google Maps',
        'general_seo': 'General SEO - Meta tags, canonical URLs, structured data',
        'blogging': 'Blogging - Article schema, authors, categories, tags',
        'ecommerce': 'E-commerce - Product schema, pricing, inventory, reviews',
        'news_media': 'News/Media - NewsArticle schema, AMP, publication metadata',
        'technical_seo': 'Technical SEO - Core Web Vitals, performance, mobile-friendliness',
        'competitor': 'Competitor Analysis - Multi-site comparison and benchmarking',
    }
    
    for crawler_type in crawlers:
        description = descriptions.get(crawler_type, 'N/A')
        print(f"  • {crawler_type:<20} - {description}")
    print()


def create_and_run_crawler(crawler_type: str, start_urls: list, config: dict = None):
    """
    Create and run a specific crawler type.
    
    Args:
        crawler_type: Type of crawler to create ('local_seo', 'general_seo', etc.)
        start_urls: List of URLs to crawl
        config: Configuration dictionary (if None, loads from file)
    
    Returns:
        Tuple of (crawl_data, report)
    """
    if config is None:
        config = load_config_wrapper()
    
    print(f"\n{'='*60}")
    print(f"Creating {crawler_type} crawler...")
    print(f"{'='*60}\n")
    
    # Create crawler instance
    crawler = create_crawler(crawler_type, config)
    
    # Run crawl
    print(f"Starting crawl from: {start_urls}")
    crawl_data = crawler.crawl(start_urls)
    
    print(f"✓ Crawl complete! Found {len(crawl_data)} pages.\n")
    
    # Generate report
    print("Generating analysis report...")
    report = crawler.generate_report(include_analysis=True)
    crawler.save_report(report)
    
    # Export data
    print("Exporting data to multiple formats...")
    exports = crawler.export_all_formats(include_analysis=True)
    
    for fmt, file_path in exports.items():
        print(f"  ✓ {fmt.upper()}: {file_path}")
    
    return crawl_data, report


def main():
    """Main entry point for interactive use."""
    config = load_config_wrapper()
    
    print("\n" + "="*60)
    print("Advertools SEO Crawler System")
    print("="*60)
    
    list_available_crawlers()
    
    print("Available Functions:")
    print("-" * 60)
    print("  create_and_run_crawler(crawler_type, start_urls, config=None)")
    print("    Run a single crawler and generate all reports")
    print()
    print("  create_crawler(crawler_type, config)")
    print("    Create crawler instance for manual control")
    print()
    print("  ConcurrentCrawlerManager(max_concurrent=3)")
    print("    Run multiple crawlers simultaneously")
    print()
    print("  load_config_wrapper()")
    print("    Load configuration from YAML and environment")
    print()
    print("Command Line Usage:")
    print("-" * 60)
    print("  python cli.py crawl --crawler-type general_seo --url https://example.com")
    print("  python cli.py crawl --crawler-type technical_seo --url https://example.com --measure-vitals")
    print("  python cli.py list-crawlers")
    print("  python cli.py cleanup --dry-run")
    print("  python cli.py stats")
    print()
    print("Starting interactive shell. Use Ctrl+D or exit() to quit.")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
    
    # Start interactive Python shell
    import code
    code.interact(local=globals())

