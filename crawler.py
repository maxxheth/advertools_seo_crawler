#!/usr/bin/env python3
"""
Advertools SEO Crawler - Main Script
"""
import os
import yaml
import advertools as adv
from pathlib import Path


def load_config(config_path: str = None) -> dict:
    """Load configuration from YAML file."""
    if config_path is None:
        config_path = os.getenv('CONFIG_PATH', '/app/config/config.yaml')
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config


def run_sitemap_analysis(config: dict):
    """Run sitemap analysis based on configuration."""
    sitemap_config = config.get('sitemap', {})
    urls = sitemap_config.get('urls', [])
    
    if not urls:
        print("No sitemap URLs configured.")
        return
    
    print(f"Analyzing sitemaps: {urls}")
    sitemap_df = adv.sitemap_to_df(
        sitemap_config['urls'],
        recursive=sitemap_config.get('recursive', True)
    )
    
    output_file = sitemap_config.get('output_file', '/app/output/sitemap_data.jl')
    sitemap_df.to_json(output_file, orient='records', lines=True)
    print(f"Sitemap data saved to: {output_file}")
    print(f"Total URLs found: {len(sitemap_df)}")


def run_crawler(config: dict):
    """Run website crawler based on configuration."""
    crawl_config = config.get('crawl', {})
    start_urls = crawl_config.get('start_urls', [])
    
    if not start_urls:
        print("No start URLs configured for crawling.")
        return
    
    output_file = crawl_config.get('output_file', '/app/output/crawl_output.jl')
    
    print(f"Starting crawl from: {start_urls}")
    
    # Prepare custom settings
    custom_settings = crawl_config.get('custom_settings', {})
    
    adv.crawl(
        url_list=start_urls,
        output_file=output_file,
        follow_links=crawl_config.get('follow_links', True),
        css_selectors=crawl_config.get('css_selectors', []),
        xpath_selectors=crawl_config.get('xpath_selectors', []),
        custom_settings=custom_settings
    )
    
    print(f"Crawl completed. Output saved to: {output_file}")


def main():
    """Main entry point for the crawler."""
    print("=" * 60)
    print("Advertools SEO Crawler")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    
    # Create output directory if it doesn't exist
    Path("/app/output").mkdir(parents=True, exist_ok=True)
    
    # You can uncomment the function you want to run
    # run_sitemap_analysis(config)
    # run_crawler(config)
    
    print("\nCrawler script loaded. Available functions:")
    print("  - run_sitemap_analysis(config)")
    print("  - run_crawler(config)")
    print("\nUse Python interactive mode to run specific functions.")
    print("Example: docker-compose exec advertools python -i crawler.py")


if __name__ == "__main__":
    main()
