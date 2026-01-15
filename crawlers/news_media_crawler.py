"""
News/Media Crawler - Specialized for news and media sites
"""
from typing import Dict, List, Any
import pandas as pd
from crawlers.base_crawler import BaseCrawler


class NewsMediaCrawler(BaseCrawler):
    """
    Crawler specialized for news and media site analysis.
    Focuses on NewsArticle schema, AMP pages, bylines, and publication metrics.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config, crawler_type="news_media")

    def get_css_selectors(self) -> List[str]:
        """Return CSS selectors for news/media elements."""
        return [
            '[itemtype*="NewsArticle"]',
            '[itemtype*="ReportageNewsArticle"]',
            '[itemtype*="Article"]',
            'link[rel="amphtml"]',
            '.byline',
            '.author-name',
            '[itemprop="author"]',
            'time[datetime]',
            '.article-date',
            '[itemprop="datePublished"]',
            '[itemprop="dateModified"]',
            '.article-section',
            '.category',
            '[itemprop="articleSection"]',
            'video',
            '.video-player',
            '.image-gallery',
            '.source',
            '.attribution',
            '[itemprop="headline"]',
            '[itemprop="description"]',
        ]

    def get_xpath_selectors(self) -> List[str]:
        """Return XPath selectors for news/media elements."""
        return [
            '//link[@rel="amphtml"]/@href',
            '//span[@itemprop="author"]',
            '//time[@datetime]/@datetime',
            '//span[@itemprop="datePublished"]',
            '//span[@itemprop="articleSection"]',
            '//h1[@itemprop="headline"]',
        ]

    def validate_results(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate news/media elements.

        Args:
            df: DataFrame with crawl results

        Returns:
            Dictionary with validation results
        """
        validation = {
            "total_articles": len(df),
            "articles_with_schema": len(df[df.get("itemtype", "").str.contains("NewsArticle|Article", case=False, na=False)]),
            "articles_with_amp": len(df[df.get("amphtml", "").notna()]),
            "articles_with_byline": len(df[df.get("author", "").notna()]),
            "articles_with_publish_date": len(df[df.get("datePublished", "").notna()]),
            "articles_with_section": len(df[df.get("articleSection", "").notna()]),
            "articles_with_videos": len(df[df.get("video", "").notna()]),
            "articles_with_images": len(df[df.get("image", "").notna()]),
            "articles_with_updated_date": len(df[df.get("dateModified", "").notna()]),
        }
        return validation

    def analyze_results(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze news/media metrics and publication frequency.

        Args:
            df: DataFrame with crawl results

        Returns:
            Dictionary with analysis results
        """
        analysis = {
            "content_quality_score": 0.0,
            "article_schema_coverage": f"{(len(df[df.get('itemtype', '').str.contains('NewsArticle|Article', case=False, na=False)]) / len(df) * 100):.1f}%",
            "amp_page_coverage": f"{(len(df[df.get('amphtml', '').notna()]) / len(df) * 100):.1f}%",
            "byline_coverage": f"{(len(df[df.get('author', '').notna()]) / len(df) * 100):.1f}%",
            "publish_date_coverage": f"{(len(df[df.get('datePublished', '').notna()]) / len(df) * 100):.1f}%",
            "section_coverage": f"{(len(df[df.get('articleSection', '').notna()]) / len(df) * 100):.1f}%",
            "multimedia_coverage": f"{(len(df[df.get('video', '').notna() | df.get('image', '').notna()]) / len(df) * 100):.1f}%",
            "mobile_optimized": f"{(len(df[df.get('amphtml', '').notna()]) / len(df) * 100):.1f}% (AMP)",
            "average_article_length": df.get("text", "").str.len().mean(),
            "unique_authors": df.get("author", "").nunique(),
            "article_sections": df.get("articleSection", "").nunique(),
        }

        # Calculate content quality score
        score = 0
        checks = [
            ("article_schema_coverage", 0.15),
            ("byline_coverage", 0.15),
            ("publish_date_coverage", 0.15),
            ("section_coverage", 0.15),
            ("multimedia_coverage", 0.15),
            ("amp_page_coverage", 0.25),
        ]

        for check, weight in checks:
            coverage = float(analysis.get(check, "0%").rstrip("%"))
            score += (coverage / 100) * weight * 100

        analysis["content_quality_score"] = round(score, 2)

        return analysis
