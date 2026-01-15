"""
Blogging Crawler - Specialized for blog and content analysis
"""
from typing import Dict, List, Any
import pandas as pd
from crawlers.base_crawler import BaseCrawler


class BloggingCrawler(BaseCrawler):
    """
    Crawler specialized for blog and content analysis.
    Focuses on article schema, author info, categories, tags, and content metrics.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config, crawler_type="blogging")

    def get_css_selectors(self) -> Dict[str, str]:
        """Return CSS selectors for blogging elements."""
        return {
            'article_schema': '[itemtype*="Article"]',
            'blog_posting': '[itemtype*="BlogPosting"]',
            'news_article': '[itemtype*="NewsArticle"]',
            'author_class': '.author',
            'byline': '.byline',
            'author_rel': '[rel="author"]',
            'author_prop': '[itemprop="author"]',
            'time_datetime': 'time[datetime]',
            'published_date': '.published-date',
            'modified_date': '.modified-date',
            'date_published_prop': '[itemprop="datePublished"]',
            'date_modified_prop': '[itemprop="dateModified"]',
            'category': '.category',
            'tag': '.tag',
            'category_rel': '[rel="category"]',
            'tag_rel': '[rel="tag"]',
            'social_share': '.social-share',
            'share_button': '.share-button',
            'related_posts': '.related-posts',
            'recommended': '.recommended',
            'comment_count': '.comment-count',
            'comments': '#comments',
            'reading_time': '.reading-time',
            'headline_prop': '[itemprop="headline"]',
            'article_body_prop': '[itemprop="articleBody"]',
        }

    def get_xpath_selectors(self) -> Dict[str, str]:
        """Return XPath selectors for blogging elements."""
        return {
            'author': '//span[@itemprop="author"]',
            'datetime': '//time[@datetime]/@datetime',
            'date_published': '//span[@itemprop="datePublished"]/@content',
            'date_modified': '//span[@itemprop="dateModified"]/@content',
            'category': '//span[@class="category"]',
            'tag': '//span[@class="tag"]',
            'article_body': '//div[@itemprop="articleBody"]',
        }

    def validate_results(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate blog/content elements.

        Args:
            df: DataFrame with crawl results

        Returns:
            Dictionary with validation results
        """
        validation = {
            "total_articles": len(df),
            "articles_with_schema": len(df[df.get("itemtype", "").str.contains("Article", case=False, na=False)]),
            "articles_with_author": len(df[df.get("author", "").notna()]),
            "articles_with_publish_date": len(df[df.get("datePublished", "").notna()]),
            "articles_with_modified_date": len(df[df.get("dateModified", "").notna()]),
            "articles_with_categories": len(df[df.get("category", "").notna()]),
            "articles_with_tags": len(df[df.get("tag", "").notna()]),
            "articles_with_related_content": len(df[df.get("relatedLink", "").notna()]),
            "articles_with_comments": len(df[df.get("comment", "").notna()]),
        }
        return validation

    def analyze_results(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze blogging/content metrics.

        Args:
            df: DataFrame with crawl results

        Returns:
            Dictionary with analysis results
        """
        analysis = {
            "content_completeness_score": 0.0,
            "article_schema_coverage": f"{(len(df[df.get('itemtype', '').str.contains('Article', case=False, na=False)]) / len(df) * 100):.1f}%",
            "author_coverage": f"{(len(df[df.get('author', '').notna()]) / len(df) * 100):.1f}%",
            "publish_date_coverage": f"{(len(df[df.get('datePublished', '').notna()]) / len(df) * 100):.1f}%",
            "category_coverage": f"{(len(df[df.get('category', '').notna()]) / len(df) * 100):.1f}%",
            "tag_coverage": f"{(len(df[df.get('tag', '').notna()]) / len(df) * 100):.1f}%",
            "average_article_length": df.get("text", "").str.len().mean(),
            "articles_with_images": len(df[df.get("img", "").notna()]),
            "updated_articles_ratio": f"{(len(df[df.get('dateModified', '').notna()]) / len(df[df.get('datePublished', '').notna()]) * 100):.1f}%",
            "content_freshness": "Recent" if df.get("datePublished", "").notna().sum() > 0 else "Unknown",
        }

        # Calculate content completeness score
        score = 0
        checks = [
            ("article_schema_coverage", 0.2),
            ("author_coverage", 0.15),
            ("publish_date_coverage", 0.2),
            ("category_coverage", 0.15),
            ("tag_coverage", 0.15),
        ]

        for check, weight in checks:
            coverage = float(analysis.get(check, "0%").rstrip("%"))
            score += (coverage / 100) * weight * 100

        analysis["content_completeness_score"] = round(score, 2)

        return analysis
