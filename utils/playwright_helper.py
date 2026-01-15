"""
Playwright Helper - Browser automation for technical SEO measurements
"""
from typing import Dict, List, Optional
from pathlib import Path


class PlaywrightHelper:
    """
    Helper class for Playwright browser automation.
    Handles Core Web Vitals measurement, screenshots, and responsive testing.
    """

    def __init__(self, screenshots_dir: str):
        """
        Initialize Playwright helper.

        Args:
            screenshots_dir: Directory to save screenshots
        """
        self.screenshots_dir = Path(screenshots_dir)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.browser = None
        self.context = None

    async def measure_core_web_vitals(self, url: str) -> Dict[str, float]:
        """
        Measure Core Web Vitals for a URL.

        Args:
            url: URL to measure

        Returns:
            Dictionary with LCP, FID, CLS measurements
        """
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            raise ImportError("playwright is required. Install with: pip install playwright")

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            # Inject script to collect Web Vitals
            await page.evaluate("""
                window.vitals = {};
                
                // Largest Contentful Paint
                const observer = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        window.vitals.lcp = entry.renderTime || entry.loadTime;
                    }
                });
                observer.observe({type: 'largest-contentful-paint', buffered: true});

                // Cumulative Layout Shift
                let cls = 0;
                new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        if (!entry.hadRecentInput) {
                            cls += entry.value;
                        }
                    }
                    window.vitals.cls = cls;
                }).observe({type: 'layout-shift', buffered: true});

                // First Input Delay
                new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        window.vitals.fid = entry.processingDuration;
                    }
                }).observe({type: 'first-input', buffered: true});
            """)

            await page.goto(url, wait_until='networkidle')
            await page.wait_for_timeout(2000)

            vitals = await page.evaluate("() => window.vitals")

            await browser.close()

            return {
                'lcp': vitals.get('lcp', 0),
                'fid': vitals.get('fid', 0),
                'cls': vitals.get('cls', 0),
            }

    async def take_screenshot(self, url: str, viewport: Optional[Dict[str, int]] = None) -> str:
        """
        Take screenshot of a URL.

        Args:
            url: URL to screenshot
            viewport: Viewport size (width, height)

        Returns:
            Path to saved screenshot
        """
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            raise ImportError("playwright is required. Install with: pip install playwright")

        async with async_playwright() as p:
            browser = await p.chromium.launch()

            # Set viewport for device simulation
            if viewport is None:
                viewport = {'width': 1920, 'height': 1080}

            context = await browser.new_context(viewport=viewport)
            page = await context.new_page()

            await page.goto(url, wait_until='networkidle')

            # Generate safe filename from URL
            safe_name = url.replace('https://', '').replace('http://', '').replace('/', '_')
            screenshot_path = self.screenshots_dir / f"{safe_name}.png"

            await page.screenshot(path=str(screenshot_path), full_page=True)

            await browser.close()

            return str(screenshot_path)

    async def check_responsiveness(self, url: str, mode: str = "all") -> Dict[str, Dict]:
        """
        Check responsiveness across device types.

        Args:
            url: URL to check
            mode: Responsiveness check mode (all, mobile, desktop, tablet)

        Returns:
            Dictionary with screenshots for each device type
        """
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            raise ImportError("playwright is required. Install with: pip install playwright")

        viewports = {
            "mobile": {"width": 375, "height": 667, "device_scale_factor": 2},
            "tablet": {"width": 768, "height": 1024, "device_scale_factor": 2},
            "desktop": {"width": 1920, "height": 1080},
        }

        # Determine which viewports to test
        if mode == "all":
            test_modes = ["mobile", "tablet", "desktop"]
        else:
            test_modes = [mode]

        results = {}

        for device_type in test_modes:
            try:
                screenshot_path = await self.take_screenshot(url, viewport=viewports[device_type])
                results[device_type] = {
                    "screenshot": screenshot_path,
                    "viewport": viewports[device_type],
                    "success": True
                }
            except Exception as e:
                results[device_type] = {
                    "error": str(e),
                    "success": False
                }

        return results

    async def measure_performance_metrics(self, url: str) -> Dict[str, float]:
        """
        Measure performance metrics for a URL.

        Args:
            url: URL to measure

        Returns:
            Dictionary with performance metrics
        """
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            raise ImportError("playwright is required. Install with: pip install playwright")

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            # Measure navigation timing
            await page.goto(url, wait_until='networkidle')

            timing = await page.evaluate("""() => {
                const nav = performance.getEntriesByType('navigation')[0];
                return {
                    dns: nav.domainLookupEnd - nav.domainLookupStart,
                    tcp: nav.connectEnd - nav.connectStart,
                    ttfb: nav.responseStart - nav.requestStart,
                    domLoad: nav.domContentLoadedEventEnd - nav.domContentLoadedEventStart,
                    pageLoad: nav.loadEventEnd - nav.loadEventStart,
                    totalTime: nav.loadEventEnd - nav.fetchStart,
                };
            }""")

            await browser.close()

            return timing
