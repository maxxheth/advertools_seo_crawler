#!/usr/bin/env python3
"""
Example: Real-time Crawl Monitoring with WebSocket
Monitor crawl progress in real-time via WebSocket
"""
import asyncio
from utils.config_loader import load_config
from crawlers.crawler_factory import create_crawler
from utils.websocket_server import WebSocketManager

async def main():
    # Load configuration
    config = load_config()
    
    # Initialize WebSocket manager
    ws_manager = WebSocketManager(
        host=config['watch_settings']['websocket_host'],
        port=config['watch_settings']['websocket_port']
    )
    
    # Start WebSocket server
    await ws_manager.start()
    
    print("=" * 60)
    print("Real-time Crawl Monitoring")
    print("=" * 60)
    print(f"WebSocket server running on ws://localhost:{config['watch_settings']['websocket_port']}")
    print()
    
    # Create crawler
    crawler = create_crawler('general_seo', config)
    
    # Set WebSocket manager
    crawler.websocket_manager = ws_manager
    
    # Start crawl
    start_urls = ["https://example.com"]
    
    print("Starting crawl...")
    await ws_manager.send_crawl_start('general_seo', start_urls)
    
    try:
        crawl_data = crawler.crawl(start_urls)
        
        print(f"\n✓ Crawl complete! {len(crawl_data)} pages crawled")
        
        # Send completion event
        await ws_manager.send_crawl_complete('general_seo', len(crawl_data), 0)
        
        # Generate report
        report = crawler.generate_report(include_analysis=True)
        crawler.save_report(report)
        
        exports = crawler.export_all_formats(include_analysis=True)
        for fmt, file_path in exports.items():
            print(f"  ✓ {fmt.upper()}: {file_path}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        await ws_manager.send_error('general_seo', str(e))
    
    finally:
        # Cleanup
        await ws_manager.stop()
        print("\n✓ Monitoring session complete!")


if __name__ == "__main__":
    print("Note: Connect a client to ws://localhost:8765 to receive events")
    print()
    asyncio.run(main())
