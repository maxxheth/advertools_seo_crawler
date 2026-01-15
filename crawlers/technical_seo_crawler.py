"""
Technical SEO Crawler - Specialized for technical SEO analysis
"""
from typing import Dict, List, Any, Optional
import pandas as pd
from crawlers.base_crawler import BaseCrawler


class TechnicalSEOCrawler(BaseCrawler):
    """
    Crawler specialized for technical SEO analysis.
    Focuses on Core Web Vitals, performance metrics, mobile-friendliness, redirects, and broken links.
    Supports Playwright integration for performance measurement and responsive testing.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config, crawler_type="technical_seo")
        self.measure_vitals = False
        self.take_screenshots = False
        self.check_responsiveness = "all"  # all, mobile, desktop, tablet
        self.playwright_helper = None

    def get_css_selectors(self) -> Dict[str, str]:
        """Return CSS selectors for technical SEO elements."""
        return {
            'canonical': 'link[rel="canonical"]',
            'viewport': 'meta[name="viewport"]',
            'robots': 'meta[name="robots"]',
            'alternate': 'link[rel="alternate"]',
            'json_ld': 'script[type="application/ld+json"]',
            'nosnippet': '[data-nosnippet]',
            'refresh': 'meta[http-equiv="refresh"]',
            'preconnect': 'link[rel="preconnect"]',
            'dns_prefetch': 'link[rel="dns-prefetch"]',
            'prefetch': 'link[rel="prefetch"]',
            'preload': 'link[rel="preload"]',
            'stylesheet': 'link[rel="stylesheet"]',
            'script': 'script[src]',
            'lazy_img': 'img[loading="lazy"]',
            'img': 'img[src]',
            'external_links': 'a[href*="http"]',
        }

    def get_xpath_selectors(self) -> Dict[str, str]:
        """Return XPath selectors for technical SEO elements."""
        return {
            'canonical_href': '//link[@rel="canonical"]/@href',
            'viewport_content': '//meta[@name="viewport"]/@content',
            'robots_content': '//meta[@name="robots"]/@content',
            'alternate_hreflang': '//link[@rel="alternate"]/@hreflang',
            'json_ld': '//script[@type="application/ld+json"]',
            'img_alt': '//img/@alt',
            'all_links': '//a/@href',
        }

    def set_playwright_options(
        self,
        measure_vitals: bool = False,
        take_screenshots: bool = False,
        check_responsiveness: str = "all"
    ):
        """
        Configure Playwright options for technical measurement.

        Args:
            measure_vitals: Whether to measure Core Web Vitals and performance
            take_screenshots: Whether to capture screenshots
            check_responsiveness: Responsive check mode (all, mobile, desktop, tablet)
        """
        self.measure_vitals = measure_vitals
        self.take_screenshots = take_screenshots
        self.check_responsiveness = check_responsiveness

        if measure_vitals or take_screenshots or check_responsiveness != "all":
            from utils.playwright_helper import PlaywrightHelper
            self.playwright_helper = PlaywrightHelper(self.screenshots_dir)

    def validate_results(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate technical SEO elements.

        Args:
            df: DataFrame with crawl results

        Returns:
            Dictionary with validation results
        """
        validation = {
            "total_pages": len(df),
            "pages_with_canonical": len(df[df.get("canonical", "").notna()]),
            "pages_with_viewport": len(df[df.get("viewport", "").notna()]),
            "pages_with_robots_meta": len(df[df.get("robots", "").notna()]),
            "pages_with_alt_text": len(df[df.get("img_alt", "").notna()]),
            "redirect_chains": len(df[df.get("redirect", "").notna()]),
            "broken_links": 0,
            "pages_mobile_friendly": len(df[df.get("viewport", "").notna()]),
            "pages_with_schema": len(df[df.get("itemscope", "").notna()]),
            "pages_with_https": len(df[df.get("url", "").str.startswith("https", na=False)]),
        }

        return validation

    def analyze_results(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze technical SEO metrics.

        Args:
            df: DataFrame with crawl results

        Returns:
            Dictionary with analysis results
        """
        analysis = {
            "technical_seo_score": 0.0,
            "mobile_friendliness": f"{(len(df[df.get('viewport', '').notna()]) / len(df) * 100):.1f}%",
            "https_coverage": f"{(len(df[df.get('url', '').str.startswith('https', na=False)]) / len(df) * 100):.1f}%",
            "canonical_coverage": f"{(len(df[df.get('canonical', '').notna()]) / len(df) * 100):.1f}%",
            "robots_meta_coverage": f"{(len(df[df.get('robots', '').notna()]) / len(df) * 100):.1f}%",
            "schema_markup_coverage": f"{(len(df[df.get('itemscope', '').notna()]) / len(df) * 100):.1f}%",
            "average_page_size": df.get("size", pd.Series()).apply(lambda x: int(x) if isinstance(x, (int, float)) else 0).mean(),
            "pages_with_redirects": len(df[df.get("redirect", "").notna()]),
            "crawlability_score": 0.0,
        }

        # Add performance metrics if measure_vitals is enabled
        if self.measure_vitals and "core_web_vitals" in df.columns:
            analysis["core_web_vitals"] = {
                "avg_lcp": df.get("lcp", pd.Series()).mean(),
                "avg_fid": df.get("fid", pd.Series()).mean(),
                "avg_cls": df.get("cls", pd.Series()).mean(),
            }

        # Add responsiveness data if available
        if self.take_screenshots and "screenshots" in df.columns:
            analysis["screenshots_captured"] = len(df[df.get("screenshots", "").notna()])

        # Calculate technical SEO score
        score = 0
        checks = [
            ("mobile_friendliness", 0.25),
            ("https_coverage", 0.2),
            ("canonical_coverage", 0.15),
            ("robots_meta_coverage", 0.15),
            ("schema_markup_coverage", 0.25),
        ]

        for check, weight in checks:
            coverage = float(analysis.get(check, "0%").rstrip("%"))
            score += (coverage / 100) * weight * 100

        analysis["technical_seo_score"] = round(score, 2)

        return analysis
