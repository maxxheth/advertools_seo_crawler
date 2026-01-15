#!/usr/bin/env python3
"""
Example: Website Crawling
"""
import advertools as adv

# Define the URL to crawl
start_url = "https://example.com"
output_file = "/app/output/example_crawl.jl"

# Crawl the website
adv.crawl(
    url_list=[start_url],
    output_file=output_file,
    follow_links=True,
    css_selectors=[
        'h1',
        'h2',
        'h3',
        'title',
        'meta[name="description"]',
    ],
    custom_settings={
        'USER_AGENT': 'Mozilla/5.0 (compatible; AdvertoolsCrawler/1.0)',
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': 8,
        'DOWNLOAD_DELAY': 0.5,
        'DEPTH_LIMIT': 2,
    }
)

print(f"Crawl completed! Check output at: {output_file}")
