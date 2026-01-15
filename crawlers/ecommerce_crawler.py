"""
E-commerce Crawler - Specialized for e-commerce site analysis
"""
from typing import Dict, List, Any
import pandas as pd
from crawlers.base_crawler import BaseCrawler


class EcommerceCrawler(BaseCrawler):
    """
    Crawler specialized for e-commerce site analysis.
    Focuses on product schema, pricing, inventory, reviews, and breadcrumbs.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config, crawler_type="ecommerce")

    def get_css_selectors(self) -> List[str]:
        """Return CSS selectors for e-commerce elements."""
        return [
            '[itemtype*="Product"]',
            '[itemprop="offers"]',
            '[itemprop="price"]',
            '[itemprop="priceCurrency"]',
            '[itemprop="availability"]',
            '[itemprop="sku"]',
            '[itemprop="productID"]',
            '.breadcrumb',
            '[itemtype*="BreadcrumbList"]',
            '[itemprop="review"]',
            '[itemprop="aggregateRating"]',
            '.product-rating',
            '.star-rating',
            '.add-to-cart',
            '.buy-now',
            '.product-image',
            '.product-gallery',
            '[itemprop="image"]',
            '.product-variant',
            '.product-option',
        ]

    def get_xpath_selectors(self) -> List[str]:
        """Return XPath selectors for e-commerce elements."""
        return [
            '//span[@itemprop="price"]',
            '//span[@itemprop="priceCurrency"]',
            '//span[@itemprop="availability"]',
            '//span[@itemprop="sku"]',
            '//span[@itemprop="aggregateRating"]',
            '//span[@itemprop="ratingValue"]',
            '//link[@itemtype="BreadcrumbList"]',
        ]

    def validate_results(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate e-commerce elements.

        Args:
            df: DataFrame with crawl results

        Returns:
            Dictionary with validation results
        """
        validation = {
            "total_products": len(df),
            "products_with_schema": len(df[df.get("itemtype", "").str.contains("Product", case=False, na=False)]),
            "products_with_price": len(df[df.get("price", "").notna()]),
            "products_with_currency": len(df[df.get("priceCurrency", "").notna()]),
            "products_with_availability": len(df[df.get("availability", "").notna()]),
            "products_with_sku": len(df[df.get("sku", "").notna()]),
            "products_with_breadcrumbs": len(df[df.get("breadcrumb", "").notna()]),
            "products_with_reviews": len(df[df.get("review", "").notna()]),
            "products_with_ratings": len(df[df.get("aggregateRating", "").notna()]),
            "products_with_images": len(df[df.get("image", "").notna()]),
        }
        return validation

    def analyze_results(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze e-commerce metrics and pricing.

        Args:
            df: DataFrame with crawl results

        Returns:
            Dictionary with analysis results
        """
        analysis = {
            "product_data_completeness": 0.0,
            "product_schema_coverage": f"{(len(df[df.get('itemtype', '').str.contains('Product', case=False, na=False)]) / len(df) * 100):.1f}%",
            "price_coverage": f"{(len(df[df.get('price', '').notna()]) / len(df) * 100):.1f}%",
            "availability_coverage": f"{(len(df[df.get('availability', '').notna()]) / len(df) * 100):.1f}%",
            "review_coverage": f"{(len(df[df.get('review', '').notna()]) / len(df) * 100):.1f}%",
            "breadcrumb_coverage": f"{(len(df[df.get('breadcrumb', '').notna()]) / len(df) * 100):.1f}%",
            "average_product_rating": df.get("aggregateRating", pd.Series()).apply(
                lambda x: float(str(x).split()[0]) if isinstance(x, str) and str(x)[0].isdigit() else None
            ).mean(),
            "products_in_stock": len(df[df.get("availability", "").str.contains("InStock", case=False, na=False)]),
            "products_out_of_stock": len(df[df.get("availability", "").str.contains("OutOfStock", case=False, na=False)]),
            "average_product_images": df.get("image", []).apply(lambda x: len(x) if isinstance(x, list) else (1 if pd.notna(x) else 0)).mean(),
        }

        # Calculate product data completeness
        score = 0
        checks = [
            ("product_schema_coverage", 0.2),
            ("price_coverage", 0.25),
            ("availability_coverage", 0.2),
            ("review_coverage", 0.15),
            ("breadcrumb_coverage", 0.2),
        ]

        for check, weight in checks:
            coverage = float(analysis.get(check, "0%").rstrip("%"))
            score += (coverage / 100) * weight * 100

        analysis["product_data_completeness"] = round(score, 2)

        return analysis
