#!/usr/bin/env python3
"""
Example: Competitor Analysis
Compare multiple competitor websites side-by-side
"""
from utils.config_loader import load_config
from crawlers.competitor_crawler import CompetitorCrawler

# Load configuration
config = load_config()

# Create crawler instance
crawler = CompetitorCrawler(config)

# Define competitors with page limits
competitors = {
    "https://competitor1.com": 500,
    "https://competitor2.com": 500,
    "https://competitor3.com": 500,
}

crawler.set_competitors(competitors)

print("=" * 60)
print("Competitor Analysis Example")
print("=" * 60)
print("Analyzing competitors:")
for domain, limit in competitors.items():
    print(f"  • {domain} (up to {limit} pages)")
print()

# Crawl each competitor
all_results = {}

for domain, page_limit in competitors.items():
    print(f"\nCrawling {domain}...")
    
    # Update page limit
    config['crawl_settings']['default_page_limit'] = page_limit
    
    # Crawl
    crawl_data = crawler.crawl([domain])
    all_results[domain] = crawl_data
    
    print(f"✓ Crawled {len(crawl_data)} pages from {domain}")

# Generate comparison report
print("\n" + "=" * 60)
print("Competitive Analysis")
print("=" * 60)

comparison = crawler.compare_competitors(all_results)

print("\nComparison Results:")
for domain, metrics in comparison['competitors'].items():
    print(f"\n{domain}:")
    for metric, value in metrics.items():
        print(f"  {metric}: {value}")

# Generate detailed report
report = crawler.generate_report(include_analysis=True)

print("\nAnalysis Results:")
for key, value in report['analysis'].items():
    print(f"  {key}: {value}")

# Export data
print("\nExporting comparison data...")
exports = crawler.export_all_formats(include_analysis=True)

for fmt, file_path in exports.items():
    print(f"  ✓ {fmt.upper()}: {file_path}")

print("\n✓ Competitor analysis complete!")
