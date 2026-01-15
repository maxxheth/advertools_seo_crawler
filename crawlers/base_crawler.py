"""
Base Crawler Class - Abstract base for all specialized crawlers
"""
import json
import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd
import advertools as adv


class BaseCrawler(ABC):
    """
    Abstract base class for all SEO crawlers.
    Provides common functionality for crawling, exporting, analysis, and reporting.
    """

    def __init__(self, config: Dict[str, Any], crawler_type: str):
        """
        Initialize the crawler.

        Args:
            config: Configuration dictionary
            crawler_type: Type of crawler (e.g., 'local_seo', 'general_seo')
        """
        self.config = config
        self.crawler_type = crawler_type
        self.crawl_data = None
        self.analysis_results = None
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.websocket_manager = None
        self._setup_paths()

    def _setup_paths(self):
        """Setup output directories."""
        self.output_dir = Path(self.config.get("output_settings", {}).get("output_path", "/app/output"))
        self.reports_dir = self.output_dir / "reports" / self.crawler_type
        self.screenshots_dir = self.output_dir / "screenshots" / self.crawler_type / self.timestamp
        
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def get_css_selectors(self) -> Dict[str, str]:
        """Return CSS selectors for this crawler type."""
        pass

    @abstractmethod
    def get_xpath_selectors(self) -> Dict[str, str]:
        """Return XPath selectors for this crawler type."""
        pass

    def get_custom_settings(self) -> Dict[str, Any]:
        """Return Scrapy custom settings for this crawler type."""
        crawler_config = self.config.get("crawler_types", {}).get(self.crawler_type, {})
        settings = crawler_config.get("custom_settings", {})
        
        # Set page limit
        page_limit = self.config.get("crawl_settings", {}).get(
            "page_limits", {}
        ).get(self.crawler_type, self.config.get("crawl_settings", {}).get("default_page_limit", 500))
        
        settings["CLOSESPIDER_PAGECOUNT"] = page_limit
        
        # SSL verification
        crawl_settings = self.config.get("crawl_settings", {})
        if not crawl_settings.get("verify_ssl", True):
            settings["ROBOTSTXT_OBEY"] = False
            settings["DOWNLOADER_CLIENT_TLS_VERBOSE_LOGGING"] = False
        
        # Timeouts and retries
        settings["DOWNLOAD_TIMEOUT"] = crawl_settings.get("timeout", 30)
        settings["RETRY_TIMES"] = crawl_settings.get("retry_count", 3)
        settings["RETRY_HTTP_CODES"] = [500, 502, 503, 504, 408, 429]
        
        return settings

    async def emit_event(self, event_type: str, data: Dict[str, Any]):
        """
        Emit event for WebSocket monitoring.

        Args:
            event_type: Type of event (e.g., 'crawl_start', 'page_crawled', 'crawl_complete')
            data: Event data
        """
        if self.websocket_manager:
            await self.websocket_manager.broadcast({
                "crawler": self.crawler_type,
                "event": event_type,
                "timestamp": datetime.now().isoformat(),
                "data": data
            })

    def crawl(self, start_urls: List[str], output_file: Optional[str] = None) -> pd.DataFrame:
        """
        Execute the crawl.

        Args:
            start_urls: List of URLs to start crawling from
            output_file: Path to save raw crawl output

        Returns:
            DataFrame with crawl results
        """
        if not output_file:
            output_file = str(self.output_dir / f"{self.crawler_type}_crawl_{self.timestamp}.jl")

        # Validate URLs
        if not start_urls:
            print("Warning: No URLs provided for crawl")
            self.crawl_data = pd.DataFrame()
            return self.crawl_data

        print(f"Starting {self.crawler_type} crawl from: {start_urls}")

        try:
            adv.crawl(
                url_list=start_urls,
                output_file=output_file,
                follow_links=self.config.get("crawl_settings", {}).get("follow_links", True),
                css_selectors=self.get_css_selectors(),
                xpath_selectors=self.get_xpath_selectors(),
                custom_settings=self.get_custom_settings()
            )

            # Load results with error handling
            if Path(output_file).exists():
                self.crawl_data = pd.read_json(output_file, lines=True)
            else:
                print(f"Warning: Output file not created: {output_file}")
                self.crawl_data = pd.DataFrame()

            # Filter out error rows (DNS failures, timeouts, etc)
            if len(self.crawl_data) > 0:
                # Remove rows where URL is actually an error message
                self.crawl_data = self.crawl_data[~self.crawl_data.get('url', '').astype(str).str.contains('lookup failed|timeout|error', case=False, na=False)]
                print(f"Crawl completed. Found {len(self.crawl_data)} valid pages.")
            else:
                print("Crawl completed. No pages found.")
            
            return self.crawl_data
            
        except Exception as e:
            print(f"Error during crawl: {e}")
            # Try to load partial results if available
            if Path(output_file).exists():
                try:
                    self.crawl_data = pd.read_json(output_file, lines=True)
                    print(f"Loaded {len(self.crawl_data)} partial results before error")
                    return self.crawl_data
                except:
                    pass
            self.crawl_data = pd.DataFrame()
            return self.crawl_data

    @abstractmethod
    def validate_results(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate crawl results.

        Args:
            df: DataFrame with crawl results

        Returns:
            Dictionary with validation results
        """
        pass

    @abstractmethod
    def analyze_results(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform analysis on crawl results.

        Args:
            df: DataFrame with crawl results

        Returns:
            Dictionary with analysis results
        """
        pass

    def generate_report(self, include_analysis: bool = True) -> Dict[str, Any]:
        """
        Generate analysis report.

        Args:
            include_analysis: Whether to include detailed analysis

        Returns:
            Report dictionary
        """
        if self.crawl_data is None or len(self.crawl_data) == 0:
            return {
                "crawler_type": self.crawler_type,
                "timestamp": self.timestamp,
                "crawl_summary": {
                    "total_urls": 0,
                    "crawl_date": datetime.now().isoformat(),
                    "error": "No valid data crawled"
                },
                "validation": {},
                "analysis": {} if include_analysis else None
            }

        report = {
            "crawler_type": self.crawler_type,
            "timestamp": self.timestamp,
            "crawl_summary": {
                "total_urls": len(self.crawl_data),
                "crawl_date": datetime.now().isoformat()
            },
            "validation": self.validate_results(self.crawl_data)
        }

        if include_analysis:
            try:
                report["analysis"] = self.analyze_results(self.crawl_data)
            except Exception as e:
                print(f"Warning: Analysis failed - {e}")
                report["analysis"] = {"error": str(e)}

        return report

    def save_report(self, report: Optional[Dict[str, Any]] = None, include_analysis: bool = True) -> str:
        """
        Save report to timestamped JSON file.

        Args:
            report: Report dictionary (if None, generates one)
            include_analysis: Whether to include analysis in generated report

        Returns:
            Path to saved report
        """
        if report is None:
            report = self.generate_report(include_analysis=include_analysis)

        report_path = self.reports_dir / f"report_{self.timestamp}.json"
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"Report saved to: {report_path}")
        return str(report_path)

    def to_csv(self, output_file: Optional[str] = None) -> str:
        """
        Export crawl data to CSV.

        Args:
            output_file: Output file path

        Returns:
            Path to saved file
        """
        if self.crawl_data is None:
            raise ValueError("No crawl data available.")

        if not output_file:
            output_file = str(self.output_dir / f"{self.crawler_type}_data_{self.timestamp}.csv")

        self.crawl_data.to_csv(output_file, index=False)
        print(f"Data exported to CSV: {output_file}")
        return output_file

    def to_jsonlines(self, output_file: Optional[str] = None) -> str:
        """
        Export crawl data to JSON Lines.

        Args:
            output_file: Output file path

        Returns:
            Path to saved file
        """
        if self.crawl_data is None:
            raise ValueError("No crawl data available.")

        if not output_file:
            output_file = str(self.output_dir / f"{self.crawler_type}_data_{self.timestamp}.jl")

        self.crawl_data.to_json(output_file, orient='records', lines=True)
        print(f"Data exported to JSON Lines: {output_file}")
        return output_file

    def to_html(self, output_file: Optional[str] = None, include_analysis: bool = True) -> str:
        """
        Export crawl data and analysis to HTML dashboard.

        Args:
            output_file: Output file path
            include_analysis: Whether to include analysis in HTML

        Returns:
            Path to saved file
        """
        if self.crawl_data is None:
            raise ValueError("No crawl data available.")

        if not output_file:
            output_file = str(self.output_dir / f"{self.crawler_type}_report_{self.timestamp}.html")

        report = self.generate_report(include_analysis=include_analysis)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{self.crawler_type} Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 10px; border-radius: 5px; }}
                .section {{ margin-top: 20px; padding: 10px; border-left: 4px solid #007bff; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #007bff; color: white; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{self.crawler_type.replace('_', ' ').title()} Report</h1>
                <p>Generated: {report['timestamp']}</p>
            </div>

            <div class="section">
                <h2>Crawl Summary</h2>
                <p><strong>Total URLs:</strong> {report['crawl_summary']['total_urls']}</p>
                <p><strong>Date:</strong> {report['crawl_summary']['crawl_date']}</p>
            </div>

            <div class="section">
                <h2>Validation Results</h2>
                <pre>{json.dumps(report['validation'], indent=2)}</pre>
            </div>

            {f'''<div class="section">
                <h2>Analysis Results</h2>
                <pre>{json.dumps(report['analysis'], indent=2)}</pre>
            </div>''' if include_analysis else ''}
        </body>
        </html>
        """

        with open(output_file, 'w') as f:
            f.write(html_content)

        print(f"HTML report exported to: {output_file}")
        return output_file

    def export_all_formats(self, include_analysis: bool = True) -> Dict[str, str]:
        """
        Export crawl data to all supported formats.

        Args:
            include_analysis: Whether to include analysis

        Returns:
            Dictionary mapping format to file path
        """
        return {
            "csv": self.to_csv(),
            "jsonlines": self.to_jsonlines(),
            "html": self.to_html(include_analysis=include_analysis),
            "report": self.save_report(include_analysis=include_analysis)
        }
