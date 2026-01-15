#!/usr/bin/env python3
"""
Example: Using S3 for Screenshot Storage
Store technical SEO screenshots in AWS S3 with presigned URLs
"""
from utils.config_loader import load_config
from crawlers.technical_seo_crawler import TechnicalSEOCrawler
from utils.storage_manager import StorageManager

# Load configuration and update to use S3
config = load_config()
config['storage']['screenshot_storage'] = 's3'

# Initialize storage manager
storage = StorageManager(config)

# Create crawler
crawler = TechnicalSEOCrawler(config)

# Configure for screenshot capture
crawler.set_playwright_options(
    measure_vitals=False,
    take_screenshots=True,
    check_responsiveness='all'
)

print("=" * 60)
print("S3 Screenshot Storage Example")
print("=" * 60)
print("Configuration:")
print(f"  Storage Backend: {config['storage']['screenshot_storage']}")
print(f"  S3 Bucket: {config['storage']['s3_bucket']}")
print(f"  S3 Region: {config['storage']['s3_region']}")
print()

# Run crawl
start_urls = ["https://example.com"]

print("Starting crawl with screenshot capture...")
crawl_data = crawler.crawl(start_urls)

print(f"\n✓ Crawled {len(crawl_data)} pages with screenshots")

# List screenshots in S3
print("\nScreenshots stored in S3:")
screenshots = storage.list_screenshots('technical_seo')
for screenshot in screenshots[:10]:  # Show first 10
    print(f"  • {screenshot}")

# Get presigned URL for a screenshot (if using S3 backend)
if isinstance(storage.backend, StorageManager.__class__):
    try:
        if screenshots:
            presigned_url = storage.backend.get_presigned_url(screenshots[0])
            print(f"\nPresigned URL for first screenshot:")
            print(f"  {presigned_url}")
    except AttributeError:
        print("\nNote: Presigned URLs only available with S3 backend")

# Generate report
report = crawler.generate_report(include_analysis=True)
crawler.save_report(report)

# Export data
exports = crawler.export_all_formats(include_analysis=True)
for fmt, file_path in exports.items():
    print(f"  ✓ {fmt.upper()}: {file_path}")

print("\n✓ S3 screenshot storage example complete!")
