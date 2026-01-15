#!/usr/bin/env python3
"""
Example: Sitemap Analysis
"""
import advertools as adv
import pandas as pd

# Analyze a sitemap
sitemap_url = "https://example.com/sitemap.xml"
sitemap_df = adv.sitemap_to_df(sitemap_url)

# Display basic info
print(f"Total URLs in sitemap: {len(sitemap_df)}")
print("\nFirst 5 URLs:")
print(sitemap_df.head())

# Save to file
output_path = "/app/output/sitemap_example.csv"
sitemap_df.to_csv(output_path, index=False)
print(f"\nSaved to: {output_path}")
