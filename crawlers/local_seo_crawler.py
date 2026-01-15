"""
Local SEO Crawler - Specialized for local business analysis
"""
from typing import Dict, List, Any
import pandas as pd
from crawlers.base_crawler import BaseCrawler


class LocalSEOCrawler(BaseCrawler):
    """
    Crawler specialized for local SEO analysis.
    Focuses on NAP consistency, LocalBusiness schema, Google Maps, and local reviews.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config, crawler_type="local_seo")

    def get_css_selectors(self) -> List[str]:
        """Return CSS selectors for local SEO elements."""
        return [
            '[itemtype*="LocalBusiness"]',
            '[itemtype*="Restaurant"]',
            '[itemtype*="Store"]',
            '[itemtype*="Organization"]',
            '.address',
            '.phone',
            '.email',
            '[itemprop="address"]',
            '[itemprop="telephone"]',
            '[itemprop="email"]',
            'iframe[src*="google.com/maps"]',
            '[itemprop="aggregateRating"]',
            '[itemprop="review"]',
            '[itemprop="openingHours"]',
            '[itemprop="areaServed"]',
            '.local-business',
            '.nap-info',
        ]

    def get_xpath_selectors(self) -> List[str]:
        """Return XPath selectors for local SEO elements."""
        return [
            '//span[@itemprop="addressLocality"]',
            '//span[@itemprop="addressRegion"]',
            '//span[@itemprop="postalCode"]',
            '//span[@itemprop="streetAddress"]',
            '//span[@itemprop="telephone"]',
            '//span[@itemprop="email"]',
            '//span[@itemprop="name"]',
        ]

    def validate_results(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate local SEO elements.

        Args:
            df: DataFrame with crawl results

        Returns:
            Dictionary with validation results
        """
        validation = {
            "has_local_business_schema": 0,
            "has_nap_data": 0,
            "has_google_maps": 0,
            "has_reviews": 0,
            "has_opening_hours": 0,
            "pages_with_address": 0,
            "pages_with_phone": 0,
            "pages_with_email": 0,
        }

        for _, row in df.iterrows():
            # Check for LocalBusiness schema
            if "itemtype" in row and "localbusiness" in str(row.get("itemtype", "")).lower():
                validation["has_local_business_schema"] += 1

            # Check for NAP data
            if row.get("address") or row.get("telephone") or row.get("email"):
                validation["has_nap_data"] += 1

            # Check for Google Maps
            if "google.com/maps" in str(row.get("iframe[src*='google.com/maps']", "")):
                validation["has_google_maps"] += 1

            # Check for reviews
            if row.get("aggregateRating") or row.get("review"):
                validation["has_reviews"] += 1

            # Check for opening hours
            if row.get("openingHours"):
                validation["has_opening_hours"] += 1

            # Count NAP elements
            if row.get("address"):
                validation["pages_with_address"] += 1
            if row.get("telephone"):
                validation["pages_with_phone"] += 1
            if row.get("email"):
                validation["pages_with_email"] += 1

        return validation

    def analyze_results(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze local SEO metrics.

        Args:
            df: DataFrame with crawl results

        Returns:
            Dictionary with analysis results
        """
        analysis = {
            "nap_consistency_score": 0.0,
            "local_business_coverage": f"{(len(df[df.get('itemtype', '').str.contains('LocalBusiness', case=False, na=False)]) / len(df) * 100):.1f}%",
            "review_pages": len(df[df.get("aggregateRating").notna()]),
            "pages_with_maps": len(df[df.get('iframe[src*="google.com/maps"]').notna()]),
            "average_rating": df.get("aggregateRating", {}).mean() if "aggregateRating" in df else None,
            "local_keywords_found": len(df[df.get('title', '').str.contains('near|local|in |at ', case=False, na=False)]),
        }

        # Calculate NAP consistency
        nap_fields = ["address", "telephone", "email"]
        nap_present = sum(1 for field in nap_fields if field in df and df[field].notna().sum() > 0)
        analysis["nap_consistency_score"] = (nap_present / len(nap_fields)) * 100

        return analysis
