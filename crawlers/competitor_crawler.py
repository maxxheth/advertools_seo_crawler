"""
Competitor Crawler - Specialized for competitive analysis
"""
from typing import Dict, List, Any
import pandas as pd
from crawlers.base_crawler import BaseCrawler


class CompetitorCrawler(BaseCrawler):
    """
    Crawler specialized for competitor analysis.
    Focuses on multi-site comparison, keyword overlap, content gaps, and benchmarking.
    Supports configurable page limits per competitor.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config, crawler_type="competitor")
        self.competitors = {}  # {domain: page_limit}
        self.comparison_results = {}

    def set_competitors(self, competitors: Dict[str, int]):
        """
        Set competitor URLs with page limits.

        Args:
            competitors: Dictionary mapping competitor URLs to page limits
        """
        self.competitors = competitors

    def get_css_selectors(self) -> Dict[str, str]:
        """Return CSS selectors for competitor analysis."""
        return {
            'title': 'title',
            'description': 'meta[name="description"]',
            'h1': 'h1',
            'h2': 'h2',
            'h3': 'h3',
            'structured_data': '[itemscope]',
            'links': 'a[href]',
            'images': 'img[alt]',
            'keyword_class': '.keyword',
            'keyword_prop': '[itemprop="keyword"]',
            'json_ld': 'script[type="application/ld+json"]',
            'og_tags': 'meta[property^="og:"]',
            'products': '.product',
            'services': '.service',
        }

    def get_xpath_selectors(self) -> Dict[str, str]:
        """Return XPath selectors for competitor analysis."""
        return {
            'title': '//title/text()',
            'description': '//meta[@name="description"]/@content',
            'h1': '//h1/text()',
            'h2': '//h2/text()',
            'links': '//a/@href',
        }

    def validate_results(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate competitor data.

        Args:
            df: DataFrame with crawl results

        Returns:
            Dictionary with validation results
        """
        validation = {
            "total_pages": len(df),
            "pages_with_title": len(df[df.get("title", "").notna()]),
            "pages_with_meta_description": len(df[df.get("description", "").notna()]),
            "pages_with_h1": len(df[df.get("h1", "").notna()]),
            "pages_with_schema": len(df[df.get("itemscope", "").notna()]),
            "internal_links_count": df.get("links_url", []).apply(lambda x: len(x) if isinstance(x, list) else 0).sum(),
            "external_links_count": df.get("links_external", []).apply(lambda x: len(x) if isinstance(x, list) else 0).sum(),
            "unique_keywords": 0,
        }

        return validation

    def analyze_results(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze competitor metrics and compare with other competitors.

        Args:
            df: DataFrame with crawl results

        Returns:
            Dictionary with analysis results
        """
        analysis = {
            "competitive_analysis_score": 0.0,
            "content_quality": f"{(len(df[df.get('title', '').notna()]) / len(df) * 100):.1f}%",
            "seo_optimization": f"{(len(df[df.get('description', '').notna()]) / len(df) * 100):.1f}%",
            "schema_implementation": f"{(len(df[df.get('itemscope', '').notna()]) / len(df) * 100):.1f}%",
            "average_internal_links": df.get("links_url", []).apply(lambda x: len(x) if isinstance(x, list) else 0).mean(),
            "average_external_links": df.get("links_external", []).apply(lambda x: len(x) if isinstance(x, list) else 0).mean(),
            "total_unique_keywords": df.get("title", "").str.split().explode().nunique(),
            "unique_outbound_domains": df.get("links_external", []).apply(
                lambda x: len(set(x)) if isinstance(x, list) else 0
            ).sum(),
            "content_freshness": "Recent" if df.get("datePublished", "").notna().sum() > 0 else "Unknown",
        }

        # Calculate competitive analysis score
        score = 0
        checks = [
            ("content_quality", 0.25),
            ("seo_optimization", 0.25),
            ("schema_implementation", 0.2),
        ]

        for check, weight in checks:
            coverage = float(analysis.get(check, "0%").rstrip("%"))
            score += (coverage / 100) * weight * 100

        analysis["competitive_analysis_score"] = round(score, 2)

        return analysis

    def compare_competitors(self, all_crawl_results: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        Compare multiple competitors side-by-side.

        Args:
            all_crawl_results: Dictionary mapping competitor domain to crawl results

        Returns:
            Comparative analysis results
        """
        comparison = {
            "comparison_date": pd.Timestamp.now().isoformat(),
            "competitors": {},
            "benchmarks": {},
        }

        # Aggregate metrics per competitor
        for domain, df in all_crawl_results.items():
            comparison["competitors"][domain] = {
                "total_pages": len(df),
                "avg_title_length": df.get("title", "").str.len().mean(),
                "avg_description_length": df.get("description", "").str.len().mean(),
                "h1_coverage": f"{(len(df[df.get('h1', '').notna()]) / len(df) * 100):.1f}%",
                "schema_coverage": f"{(len(df[df.get('itemscope', '').notna()]) / len(df) * 100):.1f}%",
            }

        return comparison
