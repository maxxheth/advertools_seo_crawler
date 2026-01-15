#!/usr/bin/env python3
"""
Example: Technical SEO Crawler
Measure Core Web Vitals, performance metrics, and responsive design
"""
from utils.config_loader import load_config
from crawlers.technical_seo_crawler import TechnicalSEOCrawler

# Load configuration
config = load_config()

# Create crawler instance
crawler = TechnicalSEOCrawler(config)

# Configure Playwright options
crawler.set_playwright_options(
    measure_vitals=True,        # Measure Core Web Vitals
    take_screenshots=True,      # Take screenshots
    check_responsiveness='all'  # Check all, mobile, desktop, tablet
)

# Crawl a website for technical SEO analysis
start_url = ["https://example.com"]

print("=" * 60)
print("Technical SEO Crawler Example")
print("=" * 60)
print("Options:")
print("  - Measure Core Web Vitals: Yes")
print("  - Take Screenshots: Yes")
print("  - Check Responsiveness: All (mobile, desktop, tablet)")
print()

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
    if key != 'core_web_vitals':
        print(f"  {key}: {value}")

if 'core_web_vitals' in report['analysis']:
    print("\nCore Web Vitals:")
    for metric, value in report['analysis']['core_web_vitals'].items():
        print(f"  {metric}: {value:.2f}ms")

# Export data
print("\nExporting data...")
exports = crawler.export_all_formats(include_analysis=True)

for fmt, file_path in exports.items():
    print(f"  ✓ {fmt.upper()}: {file_path}")

print("\n✓ Technical SEO analysis complete!")
print(f"Screenshots saved to: {crawler.screenshots_dir}")
