"""
CLI Interface - Command-line interface for the SEO crawler system
"""
import asyncio
from typing import List, Optional
import click
from utils.config_loader import load_config
from crawlers.crawler_factory import create_crawler, get_available_crawlers
from utils.concurrent_manager import ConcurrentCrawlerManager
from utils.websocket_server import WebSocketManager
from utils.report_cleanup import ReportCleanup


@click.group()
def cli():
    """Advertools SEO Crawler - Advanced web crawling and analysis tool."""
    pass


@cli.command()
@click.option('--crawler-type', multiple=True, help='Crawler types to run (can specify multiple)')
@click.option('--page-limit', type=int, default=None, help='Override default page limit')
@click.option('--url', multiple=True, required=True, help='URLs to crawl')
@click.option('--analysis', is_flag=True, default=True, help='Enable analysis reports')
@click.option('--export-format', multiple=True, type=click.Choice(['csv', 'jsonlines', 'html']), default=['jsonlines'], help='Export formats')
@click.option('--watch', is_flag=True, help='Enable real-time WebSocket monitoring')
@click.option('--measure-vitals', is_flag=True, help='Measure Core Web Vitals (technical SEO only)')
@click.option('--take-pics', is_flag=True, help='Take screenshots (technical SEO only)')
@click.option('--check-resp', type=click.Choice(['all', 'mobile', 'desktop', 'tablet']), default='all', help='Check responsiveness')
@click.option('--concurrent', is_flag=True, help='Run multiple crawlers concurrently')
@click.option('--s3-storage', is_flag=True, help='Use S3 for screenshot storage')
def crawl(crawler_type, page_limit, url, analysis, export_format, watch, measure_vitals, take_pics, check_resp, concurrent, s3_storage):
    """Run one or more crawlers."""
    config = load_config()

    # Update config with CLI options
    if page_limit:
        config['crawl_settings']['default_page_limit'] = page_limit
    if s3_storage:
        config['storage']['screenshot_storage'] = 's3'
    if watch:
        config['watch_settings']['enabled'] = True

    # Determine crawler types
    if not crawler_type:
        crawler_type = ['general_seo']  # Default to general_seo

    # Validate crawler types
    available = get_available_crawlers()
    for ct in crawler_type:
        if ct not in available:
            click.echo(f"Error: Unknown crawler type '{ct}'. Available: {', '.join(available)}", err=True)
            return

    click.echo(f"Starting crawl with: {', '.join(crawler_type)}")
    click.echo(f"URLs: {', '.join(url)}")
    click.echo(f"Export formats: {', '.join(export_format)}")

    if concurrent and len(crawler_type) > 1:
        _run_concurrent_crawlers(config, crawler_type, list(url), analysis, export_format, watch, measure_vitals, take_pics, check_resp)
    else:
        _run_sequential_crawlers(config, crawler_type, list(url), analysis, export_format, watch, measure_vitals, take_pics, check_resp)


@cli.command()
@click.option('--crawler-type', type=click.Choice(get_available_crawlers()), help='Filter by crawler type')
def list_crawlers(crawler_type):
    """List available crawler types."""
    crawlers = [crawler_type] if crawler_type else get_available_crawlers()

    click.echo("Available Crawler Types:")
    click.echo("-" * 50)

    crawler_descriptions = {
        'local_seo': 'Local SEO - NAP data, LocalBusiness schema, Google Maps',
        'general_seo': 'General SEO - Meta tags, canonical, structured data',
        'blogging': 'Blogging - Article schema, authors, categories, tags',
        'ecommerce': 'E-commerce - Product schema, pricing, reviews',
        'news_media': 'News/Media - NewsArticle schema, AMP, bylines',
        'technical_seo': 'Technical SEO - Core Web Vitals, performance, mobile',
        'competitor': 'Competitor Analysis - Multi-site comparison, benchmarking',
    }

    for ct in crawlers:
        description = crawler_descriptions.get(ct, 'N/A')
        click.echo(f"  {ct:<20} - {description}")


@cli.command()
@click.option('--days', type=int, default=None, help='Override retention days')
@click.option('--dry-run', is_flag=True, help='Show what would be deleted without deleting')
def cleanup(days, dry_run):
    """Clean up old reports based on retention policy."""
    config = load_config()

    if days:
        config['report_retention']['days'] = days

    cleanup_manager = ReportCleanup(config)
    result = cleanup_manager.cleanup_old_reports(dry_run=dry_run)

    click.echo(f"Cleanup Results:")
    click.echo(f"  Retention period: {result['retention_days']} days")
    click.echo(f"  Cutoff date: {result['cutoff_date']}")
    click.echo(f"  Files to delete: {result['files_deleted']}")
    click.echo(f"  Space freed: {result['space_freed_mb']} MB")

    if not dry_run:
        click.echo("✓ Cleanup complete!")
    else:
        click.echo("(Dry run - no files were deleted)")


@cli.command()
def stats():
    """Show statistics about stored reports."""
    config = load_config()
    cleanup_manager = ReportCleanup(config)
    stats_result = cleanup_manager.get_report_stats()

    click.echo("Report Statistics:")
    click.echo("-" * 50)
    click.echo(f"Total reports: {stats_result['total_reports']}")
    click.echo(f"Total size: {stats_result['total_size_mb']} MB")

    click.echo("\nBy Crawler Type:")
    for crawler_type, data in stats_result['by_crawler_type'].items():
        click.echo(f"  {crawler_type}: {data['count']} reports ({data['size_mb']:.2f} MB)")

    click.echo("\nBy Age:")
    click.echo(f"  < 7 days: {stats_result['by_age']['less_than_7_days']}")
    click.echo(f"  7-30 days: {stats_result['by_age']['7_to_30_days']}")
    click.echo(f"  > 30 days: {stats_result['by_age']['older_than_30_days']}")


def _run_sequential_crawlers(config, crawler_types, urls, analysis, export_formats, watch, measure_vitals, take_pics, check_resp):
    """Run crawlers sequentially."""
    for crawler_type in crawler_types:
        click.echo(f"\n[{crawler_type}] Starting crawler...")

        crawler = create_crawler(crawler_type, config)

        # Configure technical SEO options if needed
        if crawler_type == 'technical_seo':
            crawler.set_playwright_options(
                measure_vitals=measure_vitals,
                take_screenshots=take_pics,
                check_responsiveness=check_resp
            )

        # Run crawler
        try:
            df = crawler.crawl(urls)

            # Generate analysis and exports
            if analysis:
                report = crawler.save_report()
                click.echo(f"✓ Report generated: {report}")

            for fmt in export_formats:
                if fmt == 'csv':
                    csv_file = crawler.to_csv()
                    click.echo(f"✓ CSV export: {csv_file}")
                elif fmt == 'jsonlines':
                    jl_file = crawler.to_jsonlines()
                    click.echo(f"✓ JSON Lines export: {jl_file}")
                elif fmt == 'html':
                    html_file = crawler.to_html()
                    click.echo(f"✓ HTML export: {html_file}")

            click.echo(f"✓ [{crawler_type}] Crawl complete!")

        except Exception as e:
            click.echo(f"✗ Error in {crawler_type}: {e}", err=True)


def _run_concurrent_crawlers(config, crawler_types, urls, analysis, export_formats, watch, measure_vitals, take_pics, check_resp):
    """Run multiple crawlers concurrently."""
    manager = ConcurrentCrawlerManager(max_concurrent=config['crawl_settings']['max_concurrent'])

    # Submit all crawlers
    crawlers_dict = {}
    for crawler_type in crawler_types:
        crawler = create_crawler(crawler_type, config)

        if crawler_type == 'technical_seo':
            crawler.set_playwright_options(
                measure_vitals=measure_vitals,
                take_screenshots=take_pics,
                check_responsiveness=check_resp
            )

        crawlers_dict[f"{crawler_type}_1"] = (crawler, urls)

    task_ids = manager.run_multiple_crawlers(crawlers_dict)
    click.echo(f"Submitted {len(task_ids)} crawlers for concurrent execution")

    # Wait for all to complete
    results = manager.wait_for_completion()

    # Process results
    for crawler_id, result in results.items():
        if result['status'] == 'success':
            click.echo(f"✓ {crawler_id}: {result['pages_crawled']} pages crawled")
        else:
            click.echo(f"✗ {crawler_id}: {result.get('error', 'Unknown error')}", err=True)

    manager.shutdown()
    click.echo("✓ All crawlers complete!")


if __name__ == '__main__':
    cli()
