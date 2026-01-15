#!/usr/bin/env python3
"""
Example: Local SEO Crawler
Analyze local business SEO metrics, NAP consistency, and local schema markup
"""
from utils.config_loader import load_config
from crawlers.local_seo_crawler import LocalSEOCrawler

# Load configuration
config = load_config()

# Create crawler instance
crawler = LocalSEOCrawler(config)

# Crawl a local business website
start_url = ["https://example.com"]

print("=" * 60)
print("Local SEO Crawler Example")
print("=" * 60)

# Run crawl
crawl_data = crawler.crawl(start_url)

print(f"\nCrawled {len(crawl_data)} pages")

# Generate analysis
report = crawler.generate_report(include_analysis=True)

print("\nValidation Results:")
for key, value in report['validation'].items():
    print(f"  {key}: {value}")

print("\nAnalysis Results:")
for key, value in report['analysis'].items():
    print(f"  {key}: {value}")

# Export data in all formats
print("\nExporting data...")
exports = crawler.export_all_formats(include_analysis=True)

for fmt, file_path in exports.items():
    print(f"  ✓ {fmt.upper()}: {file_path}")

print("\n✓ Local SEO analysis complete!")
