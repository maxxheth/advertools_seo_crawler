#!/usr/bin/env python3
"""
Example: Concurrent Multi-Crawler Execution
Run multiple crawler types simultaneously
"""
from utils.config_loader import load_config
from crawlers.crawler_factory import create_crawler
from utils.concurrent_manager import ConcurrentCrawlerManager

# Load configuration
config = load_config()

# Initialize concurrent manager
manager = ConcurrentCrawlerManager(max_concurrent=3)

# Define crawlers to run
crawlers_config = {
    "general_seo_1": ("general_seo", ["https://example.com"]),
    "technical_seo_1": ("technical_seo", ["https://example.com"]),
    "local_seo_1": ("local_seo", ["https://example.com"]),
}

print("=" * 60)
print("Concurrent Multi-Crawler Execution")
print("=" * 60)
print(f"Running {len(crawlers_config)} crawlers concurrently...")
print()

# Create crawler instances
crawlers = {}
for task_id, (crawler_type, urls) in crawlers_config.items():
    crawler = create_crawler(crawler_type, config)
    crawlers[task_id] = (crawler, urls)

# Submit all crawlers for concurrent execution
task_ids = manager.run_multiple_crawlers(crawlers)

print("Crawlers submitted:")
for task_id, crawler_type in [(tid, crawlers_config[tid][0]) for tid in task_ids.keys()]:
    print(f"  • {task_id} ({crawler_type})")

# Wait for all crawlers to complete
print("\nWaiting for completion...")
results = manager.wait_for_completion()

# Display results
print("\n" + "=" * 60)
print("Results Summary")
print("=" * 60)

for crawler_id, result in results.items():
    status = result['status']
    if status == 'success':
        pages = result.get('pages_crawled', 'N/A')
        print(f"✓ {crawler_id}: {pages} pages crawled")
    else:
        error = result.get('error', 'Unknown error')
        print(f"✗ {crawler_id}: {error}")

# Get detailed status
print("\nDetailed Status:")
status_info = manager.get_all_status()
for crawler_id, status in status_info.items():
    print(f"\n{crawler_id}:")
    print(f"  Status: {status['status']}")
    print(f"  Duration: {status['duration']}")

# Cleanup
manager.shutdown()
print("\n✓ Concurrent execution complete!")
