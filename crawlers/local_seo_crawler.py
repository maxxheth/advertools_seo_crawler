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

    def get_css_selectors(self) -> Dict[str, str]:
        """Return CSS selectors for local SEO elements."""
        return {
            'local_business_schema': '[itemtype*="LocalBusiness"]',
            'restaurant_schema': '[itemtype*="Restaurant"]',
            'store_schema': '[itemtype*="Store"]',
            'organization_schema': '[itemtype*="Organization"]',
            'address_class': '.address',
            'phone_class': '.phone',
            'email_class': '.email',
            'address_prop': '[itemprop="address"]',
            'telephone_prop': '[itemprop="telephone"]',
            'email_prop': '[itemprop="email"]',
            'google_maps': 'iframe[src*="google.com/maps"]',
            'aggregate_rating': '[itemprop="aggregateRating"]',
            'review': '[itemprop="review"]',
            'opening_hours': '[itemprop="openingHours"]',
            'area_served': '[itemprop="areaServed"]',
            'local_business_div': '.local-business',
            'nap_info': '.nap-info',
        }

    def get_xpath_selectors(self) -> Dict[str, str]:
        """Return XPath selectors for local SEO elements."""
        return {
            'address_locality': '//span[@itemprop="addressLocality"]',
            'address_region': '//span[@itemprop="addressRegion"]',
            'postal_code': '//span[@itemprop="postalCode"]',
            'street_address': '//span[@itemprop="streetAddress"]',
            'telephone': '//span[@itemprop="telephone"]',
            'email': '//span[@itemprop="email"]',
            'name': '//span[@itemprop="name"]',
        }

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
            if 'local_business_schema' in row and row['local_business_schema']:
                validation["has_local_business_schema"] += 1

            # Check for NAP data
            if (('address_prop' in row and row['address_prop']) or 
                ('telephone_prop' in row and row['telephone_prop']) or 
                ('email_prop' in row and row['email_prop'])):
                validation["has_nap_data"] += 1

            # Check for Google Maps
            if 'google_maps' in row and row['google_maps']:
                validation["has_google_maps"] += 1

            # Check for reviews
            if (('aggregate_rating' in row and row['aggregate_rating']) or 
                ('review' in row and row['review'])):
                validation["has_reviews"] += 1

            # Check for opening hours
            if 'opening_hours' in row and row['opening_hours']:
                validation["has_opening_hours"] += 1

            # Count NAP elements
            if 'address_prop' in row and row['address_prop']:
                validation["pages_with_address"] += 1
            if 'telephone_prop' in row and row['telephone_prop']:
                validation["pages_with_phone"] += 1
            if 'email_prop' in row and row['email_prop']:
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
        # Safe column access helpers
        def safe_contains(df, col, pattern):
            if col not in df or df[col].dtype == 'object':
                return pd.Series(False, index=df.index)
            try:
                return df[col].astype(str).str.contains(pattern, case=False, na=False)
            except:
                return pd.Series(False, index=df.index)

        analysis = {
            "nap_consistency_score": 0.0,
            "local_business_coverage": "0%",
            "review_pages": 0,
            "pages_with_maps": 0,
            "average_rating": None,
            "local_keywords_found": 0,
        }

        if len(df) == 0:
            return analysis

        # Count local business schema
        local_biz = safe_contains(df, 'local_business_schema', 'LocalBusiness')
        analysis["local_business_coverage"] = f"{(local_biz.sum() / len(df) * 100):.1f}%"

        # Count review pages
        if 'review' in df:
            analysis["review_pages"] = df['review'].notna().sum()

        # Count pages with maps
        if 'google_maps' in df:
            analysis["pages_with_maps"] = df['google_maps'].notna().sum()

        # Average rating
        if 'aggregate_rating' in df:
            ratings = pd.to_numeric(df['aggregate_rating'], errors='coerce')
            if ratings.notna().sum() > 0:
                analysis["average_rating"] = float(ratings.mean())

        # Local keywords in title
        if 'title' in df:
            local_kw = safe_contains(df, 'title', r'near|local|in|at')
            analysis["local_keywords_found"] = local_kw.sum()

        # Calculate NAP consistency
        nap_fields = ["address_prop", "telephone_prop", "email_prop"]
        nap_present = sum(1 for field in nap_fields if field in df and df[field].notna().sum() > 0)
        analysis["nap_consistency_score"] = (nap_present / 3) * 100

        return analysis
