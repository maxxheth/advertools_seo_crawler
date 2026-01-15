"""
Validators - Data validation functions for crawl results
"""
from typing import Dict, List, Any
import re


def validate_nap_consistency(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate Name, Address, Phone consistency across pages.

    Args:
        data: List of page data dictionaries

    Returns:
        NAP consistency report
    """
    nap_values = {
        'names': set(),
        'addresses': set(),
        'phones': set(),
    }

    for page in data:
        if 'name' in page:
            nap_values['names'].add(page['name'])
        if 'address' in page:
            nap_values['addresses'].add(page['address'])
        if 'phone' in page:
            nap_values['phones'].add(page['phone'])

    return {
        'unique_names': len(nap_values['names']),
        'unique_addresses': len(nap_values['addresses']),
        'unique_phones': len(nap_values['phones']),
        'is_consistent': len(nap_values['names']) <= 1 and len(nap_values['addresses']) <= 1 and len(nap_values['phones']) <= 1,
    }


def validate_schema_markup(data: List[Dict[str, Any]], required_schemas: List[str]) -> Dict[str, Any]:
    """
    Validate presence of required schema markup.

    Args:
        data: List of page data dictionaries
        required_schemas: List of required schema types

    Returns:
        Schema validation report
    """
    schema_count = {schema: 0 for schema in required_schemas}

    for page in data:
        if 'itemtype' in page:
            for schema in required_schemas:
                if schema.lower() in str(page['itemtype']).lower():
                    schema_count[schema] += 1

    return {
        'schema_counts': schema_count,
        'pages_with_schema': sum(1 for page in data if 'itemtype' in page),
        'total_pages': len(data),
        'schema_coverage': f"{(sum(schema_count.values()) / len(data) * 100):.1f}%",
    }


def validate_responsive_design(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate mobile responsiveness indicators.

    Args:
        data: List of page data dictionaries

    Returns:
        Responsive design validation report
    """
    viewport_count = sum(1 for page in data if 'viewport' in page and page['viewport'])
    mobile_friendly = sum(1 for page in data if page.get('viewport') and 'width=device-width' in str(page['viewport']))

    return {
        'pages_with_viewport': viewport_count,
        'pages_mobile_friendly': mobile_friendly,
        'mobile_friendly_percentage': f"{(mobile_friendly / len(data) * 100):.1f}%",
        'needs_improvement': len(data) - mobile_friendly,
    }


def validate_link_integrity(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate link health and patterns.

    Args:
        data: List of page data dictionaries

    Returns:
        Link integrity report
    """
    broken_links = []
    external_links = []
    internal_links = []

    for page in data:
        if 'links_external' in page:
            external_links.extend(page.get('links_external', []))
        if 'links_url' in page:
            internal_links.extend(page.get('links_url', []))

    return {
        'total_internal_links': len(internal_links),
        'total_external_links': len(external_links),
        'unique_internal_domains': len(set(internal_links)),
        'unique_external_domains': len(set(external_links)),
        'broken_links_found': len(broken_links),
    }


def is_valid_url(url: str) -> bool:
    """
    Validate if string is a valid URL.

    Args:
        url: URL string to validate

    Returns:
        True if valid URL, False otherwise
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None
