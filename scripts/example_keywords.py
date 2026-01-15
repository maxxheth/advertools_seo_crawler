#!/usr/bin/env python3
"""
Example: Keyword Analysis
"""
import advertools as adv
import pandas as pd

# Generate keyword combinations
products = ['seo', 'sem', 'ppc']
words = ['tools', 'software', 'platform']
match_types = ['Exact', 'Phrase', 'Broad']

keywords_df = adv.kw_generate(
    products=products,
    words=words,
    match_types=match_types
)

print("Generated Keywords:")
print(keywords_df.head(10))
print(f"\nTotal keywords generated: {len(keywords_df)}")

# Save to file
output_path = "/app/output/keywords_example.csv"
keywords_df.to_csv(output_path, index=False)
print(f"\nSaved to: {output_path}")
