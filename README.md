# Advertools SEO Crawler - Advanced Dockerized System

A comprehensive, production-ready Dockerized system for [advertools](https://advertools.readthedocs.io/en/master/readme.html) with 7 specialized crawler types, real-time monitoring, and an interactive React/TypeScript dashboard.

## ✨ Key Features

### Specialized Crawlers
- 🏢 **Local SEO** - NAP consistency, LocalBusiness schema, Google Maps, reviews
- 🔍 **General SEO** - Meta tags, canonical URLs, structured data, on-page optimization
- 📝 **Blogging** - Article schema, authors, categories, tags, content metrics
- 🛍️ **E-commerce** - Product schema, pricing, inventory, reviews, breadcrumbs
- 📰 **News/Media** - NewsArticle schema, AMP, bylines, publication metadata
- ⚡ **Technical SEO** - Core Web Vitals, performance metrics, responsiveness, mobile-friendliness
- 🏆 **Competitor Analysis** - Multi-site comparison, benchmarking, content gaps

### Advanced Features
- 🐳 Fully Dockerized with Bun/React/TypeScript dashboard
- ⚙️ Extensible YAML configuration merged with environment variables
- 📊 Multi-format exports (CSV, JSON Lines, HTML)
- 📈 Automated analysis reports with timestamped storage
- 🔄 Real-time WebSocket monitoring and live crawl progress
- 🎬 Playwright integration for performance measurement and screenshots
- 🔀 Concurrent multi-crawler execution with resource management
- 💾 Local filesystem and AWS S3 storage support
- 🧹 Automated report cleanup with configurable retention
- 📱 Responsive dashboard with live monitoring
- 🎨 Tailwind CSS styling with Chart.js visualizations

## Quick Start

### Prerequisites
- Docker & Docker Compose
- (Optional) AWS S3 credentials for screenshot storage

### 1. Clone and Configure

```bash
# Clone the repository
git clone <repo-url>
cd advertools_seo_crawler

# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env
```

### 2. Build and Start Services

```bash
# Start Python crawler service
docker-compose up -d --build advertools

# Start dashboard (development mode)
docker-compose up -d --profile dev dashboard-dev

# Or production mode
docker-compose up -d --profile prod dashboard-prod
```

### 3. Run Your First Crawl

```bash
# Interactive Python shell
docker-compose exec advertools python -i crawler.py

# Inside the Python shell:
# crawl_data, report = create_and_run_crawler('general_seo', ['https://example.com'])
```

### 4. CLI Commands

```bash
# List available crawlers
docker-compose exec advertools python cli.py list-crawlers

# Run a single crawler
docker-compose exec advertools python cli.py crawl \
  --crawler-type general_seo \
  --url https://example.com

# Run multiple crawlers concurrently
docker-compose exec advertools python cli.py crawl \
  --crawler-type general_seo \
  --crawler-type technical_seo \
  --url https://example.com \
  --concurrent

# Run technical SEO with Core Web Vitals measurement
docker-compose exec advertools python cli.py crawl \
  --crawler-type technical_seo \
  --url https://example.com \
  --measure-vitals \
  --take-pics \
  --check-resp all

# Manage reports
docker-compose exec advertools python cli.py cleanup --dry-run
docker-compose exec advertools python cli.py stats
```

### 5. Access Dashboard

- **Development**: http://localhost:3000
- **Production**: http://localhost:80

## Architecture

```
advertools_seo_crawler/
├── crawlers/                    # Specialized crawler classes
│   ├── base_crawler.py         # Abstract base class
│   ├── local_seo_crawler.py    # Local SEO analysis
│   ├── general_seo_crawler.py  # On-page SEO
│   ├── blogging_crawler.py     # Blog content analysis
│   ├── ecommerce_crawler.py    # Product/pricing analysis
│   ├── news_media_crawler.py   # News site analysis
│   ├── technical_seo_crawler.py # Performance & metrics
│   ├── competitor_crawler.py   # Competitive analysis
│   ├── crawler_factory.py      # Dynamic instantiation
│   └── __init__.py
├── utils/                       # Utility modules
│   ├── config_loader.py        # YAML + environment config
│   ├── validators.py           # Data validation
│   ├── analyzers.py            # Analysis functions
│   ├── storage_manager.py      # Local/S3 storage
│   ├── report_cleanup.py       # Report retention
│   ├── playwright_helper.py    # Browser automation
│   ├── websocket_server.py     # Real-time monitoring
│   ├── concurrent_manager.py   # Multi-crawler execution
│   └── __init__.py
├── dashboard/                   # React/TypeScript dashboard
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── services/           # API & WebSocket services
│   │   ├── App.tsx
│   │   └── index.tsx
│   ├── package.json
│   ├── tailwind.config.js
│   ├── Dockerfile.dev
│   ├── Dockerfile.prod
│   └── nginx.conf
├── config/                      # Configuration files
│   └── config.yaml             # Main configuration
├── scripts/                     # Example scripts
│   ├── example_local_seo.py
│   ├── example_technical_seo.py
│   ├── example_competitor.py
│   ├── example_concurrent_crawl.py
│   ├── example_watch_mode.py
│   └── example_s3_storage.py
├── output/                      # Crawl outputs (mounted volume)
├── reports/                     # Timestamped reports (mounted volume)
├── screenshots/                 # Browser screenshots (mounted volume)
├── crawler.py                   # Main entry point
├── cli.py                       # Command-line interface
├── Dockerfile                   # Python image
├── docker-compose.yml           # Service orchestration
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
└── README.md                    # This file
```

## Configuration

## References

- [Advertools Documentation](https://advertools.readthedocs.io/)
- [Advertools GitHub](https://github.com/eliasdabbas/advertools)
- [Bun JavaScript Runtime](https://bun.sh/)
- [React Documentation](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Playwright](https://playwright.dev/)

## License

This Dockerized system is provided as-is. Please refer to the [advertools license](https://github.com/eliasdabbas/advertools/blob/master/LICENSE) for the underlying library.

## Support & Contributing

For issues, questions, or contributions, please refer to the repository's issue tracker and contribution guidelines.

---

**Built with ❤️ for SEO professionals and developers**
