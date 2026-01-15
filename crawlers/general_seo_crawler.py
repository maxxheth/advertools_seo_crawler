"""
General SEO Crawler - Specialized for on-page SEO analysis
"""
from typing import Dict, List, Any
import pandas as pd
from crawlers.base_crawler import BaseCrawler


class GeneralSEOCrawler(BaseCrawler):
    """
    Crawler specialized for general on-page SEO analysis.
    Focuses on meta tags, canonical URLs, structured data, and technical SEO fundamentals.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config, crawler_type="general_seo")

    def get_css_selectors(self) -> List[str]:
        """Return CSS selectors for general SEO elements."""
        return [
            'link[rel="canonical"]',
            'link[rel="alternate"]',
            'meta[name="robots"]',
            'meta[name="description"]',
            'meta[property^="og:"]',
            'meta[name^="twitter:"]',
            '[itemscope]',
            'script[type="application/ld+json"]',
            'h1',
            'h2',
            'h3',
            'img[alt]',
            'a[rel="nofollow"]',
            'a[rel="sponsored"]',
        ]

    def get_xpath_selectors(self) -> List[str]:
        """Return XPath selectors for general SEO elements."""
        return [
            '//link[@rel="canonical"]/@href',
            '//meta[@name="description"]/@content',
            '//meta[@name="robots"]/@content',
            '//h1/text()',
            '//h2/text()',
            '//title/text()',
        ]

    def validate_results(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate on-page SEO elements.

        Args:
            df: DataFrame with crawl results

        Returns:
            Dictionary with validation results
        """
        validation = {
            "total_pages": len(df),
            "pages_with_title": len(df[df.get("title", "").notna() & (df.get("title", "") != "")]),
            "pages_with_meta_description": len(df[df.get("description", "").notna()]),
            "pages_with_h1": len(df[df.get("h1", "").notna()]),
            "pages_with_canonical": len(df[df.get("canonical", "").notna()]),
            "pages_with_og_tags": len(df[df.get("og:title", "").notna() | df.get("og:description", "").notna()]),
            "pages_with_structured_data": len(df[df.get("itemscope", "").notna()]),
            "pages_with_robots_meta": len(df[df.get("robots", "").notna()]),
            "pages_missing_h1": len(df[df.get("h1", "").isna()]),
            "pages_missing_meta_description": len(df[df.get("description", "").isna()]),
        }
        return validation

    def analyze_results(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze on-page SEO metrics and scoring.

        Args:
            df: DataFrame with crawl results

        Returns:
            Dictionary with analysis results
        """
        analysis = {
            "seo_score": 0.0,
            "title_coverage": f"{(len(df[df.get('title', '').notna()]) / len(df) * 100):.1f}%",
            "meta_description_coverage": f"{(len(df[df.get('description', '').notna()]) / len(df) * 100):.1f}%",
            "h1_coverage": f"{(len(df[df.get('h1', '').notna()]) / len(df) * 100):.1f}%",
            "canonical_coverage": f"{(len(df[df.get('canonical', '').notna()]) / len(df) * 100):.1f}%",
            "structured_data_coverage": f"{(len(df[df.get('itemscope', '').notna()]) / len(df) * 100):.1f}%",
            "og_tags_coverage": f"{(len(df[df.get('og:title', '').notna()]) / len(df) * 100):.1f}%",
            "average_title_length": df.get("title", "").str.len().mean(),
            "average_description_length": df.get("description", "").str.len().mean(),
            "internal_links_count": df.get("links_url", []).apply(lambda x: len(x) if isinstance(x, list) else 0).sum(),
            "external_links_count": df.get("links_external", []).apply(lambda x: len(x) if isinstance(x, list) else 0).sum(),
        }

        # Calculate SEO score (0-100)
        score = 0
        checks = [
            ("title_coverage", 0.2),
            ("meta_description_coverage", 0.2),
            ("h1_coverage", 0.15),
            ("canonical_coverage", 0.15),
            ("structured_data_coverage", 0.15),
            ("og_tags_coverage", 0.15),
        ]

        for check, weight in checks:
            coverage = float(analysis.get(check, "0%").rstrip("%"))
            score += (coverage / 100) * weight * 100

        analysis["seo_score"] = round(score, 2)

        return analysis
