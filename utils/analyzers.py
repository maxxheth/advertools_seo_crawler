"""
Analyzers - Analysis functions for crawl results
"""
from typing import Dict, List, Any
import pandas as pd
from collections import Counter


def analyze_keyword_distribution(data: pd.DataFrame, text_column: str = 'title') -> Dict[str, Any]:
    """
    Analyze keyword distribution across pages.

    Args:
        data: DataFrame with page data
        text_column: Column to analyze

    Returns:
        Keyword analysis results
    """
    all_words = []
    
    for text in data.get(text_column, []):
        if isinstance(text, str):
            words = text.lower().split()
            all_words.extend(words)

    word_counts = Counter(all_words)
    
    return {
        'total_words': len(all_words),
        'unique_words': len(word_counts),
        'top_keywords': dict(word_counts.most_common(10)),
        'average_words_per_page': len(all_words) / len(data) if len(data) > 0 else 0,
    }


def analyze_readability_metrics(text: str) -> Dict[str, Any]:
    """
    Calculate basic readability metrics for text.

    Args:
        text: Text to analyze

    Returns:
        Readability metrics
    """
    if not text:
        return {'error': 'No text provided'}

    sentences = text.split('.')
    words = text.split()
    
    avg_sentence_length = len(words) / len(sentences) if sentences else 0
    avg_word_length = sum(len(w) for w in words) / len(words) if words else 0

    return {
        'word_count': len(words),
        'sentence_count': len(sentences),
        'paragraph_count': text.count('\n\n') + 1,
        'average_sentence_length': round(avg_sentence_length, 2),
        'average_word_length': round(avg_word_length, 2),
        'estimated_reading_time_minutes': max(1, round(len(words) / 200)),
    }


def analyze_content_gaps(your_data: pd.DataFrame, competitor_data: pd.DataFrame) -> Dict[str, Any]:
    """
    Identify content gaps compared to competitor.

    Args:
        your_data: Your site's page data
        competitor_data: Competitor's page data

    Returns:
        Content gap analysis
    """
    your_keywords = set()
    competitor_keywords = set()

    for text in your_data.get('title', []):
        if isinstance(text, str):
            your_keywords.update(text.lower().split())

    for text in competitor_data.get('title', []):
        if isinstance(text, str):
            competitor_keywords.update(text.lower().split())

    gaps = competitor_keywords - your_keywords
    advantages = your_keywords - competitor_keywords

    return {
        'your_keywords': len(your_keywords),
        'competitor_keywords': len(competitor_keywords),
        'content_gaps': list(gaps)[:20],  # Top 20 gaps
        'your_advantages': list(advantages)[:20],
        'gap_percentage': f"{(len(gaps) / len(competitor_keywords) * 100):.1f}%",
    }


def analyze_seo_performance(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synthesize SEO metrics into performance rating.

    Args:
        metrics: Dictionary of SEO metrics

    Returns:
        Performance analysis with recommendations
    """
    score = 0
    weight_total = 0

    weighted_metrics = {
        'title_coverage': 0.15,
        'meta_description_coverage': 0.15,
        'h1_coverage': 0.1,
        'mobile_friendly_percentage': 0.15,
        'schema_markup_coverage': 0.1,
        'page_speed_score': 0.2,
        'broken_links_count': -0.15,  # Negative weight
    }

    for metric, weight in weighted_metrics.items():
        if metric in metrics:
            value = metrics[metric]
            if isinstance(value, str):
                value = float(value.rstrip('%'))
            if weight < 0:
                value = 100 - value  # Invert negative metrics
            score += (value / 100) * weight * 100
            weight_total += abs(weight)

    overall_score = (score / weight_total * 100) if weight_total > 0 else 0

    # Determine rating
    if overall_score >= 80:
        rating = "Excellent"
    elif overall_score >= 60:
        rating = "Good"
    elif overall_score >= 40:
        rating = "Fair"
    else:
        rating = "Needs Improvement"

    return {
        'overall_score': round(overall_score, 2),
        'rating': rating,
        'recommendations': _generate_recommendations(metrics, overall_score),
    }


def _generate_recommendations(metrics: Dict[str, Any], score: float) -> List[str]:
    """
    Generate SEO recommendations based on metrics.

    Args:
        metrics: Dictionary of SEO metrics
        score: Overall SEO score

    Returns:
        List of recommendations
    """
    recommendations = []

    if metrics.get('title_coverage', '0%').rstrip('%') < '90':
        recommendations.append("Improve title tag coverage across pages")
    
    if metrics.get('meta_description_coverage', '0%').rstrip('%') < '90':
        recommendations.append("Add meta descriptions to more pages")
    
    if metrics.get('h1_coverage', '0%').rstrip('%') < '100':
        recommendations.append("Ensure every page has an H1 tag")
    
    if metrics.get('mobile_friendly_percentage', '0%').rstrip('%') < '95':
        recommendations.append("Improve mobile responsiveness")
    
    if score < 60:
        recommendations.append("Conduct comprehensive SEO audit")

    return recommendations[:5]  # Top 5 recommendations
