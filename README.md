# Advertools SEO Crawler - Docker Setup

A Dockerized setup for [advertools](https://advertools.readthedocs.io/en/master/readme.html), a Python library for SEO, SEM, and digital marketing analytics.

## Features

- 🐳 Fully Dockerized environment
- ⚙️ Extensible YAML configuration
- 📊 Sitemap analysis
- 🕷️ Website crawling
- 🔑 Keyword generation and analysis
- 📁 Organized output structure

## Quick Start

### 1. Build and Start the Container

```bash
docker-compose up -d --build
```

### 2. Run Example Scripts

**Sitemap Analysis:**
```bash
docker-compose exec advertools python /app/scripts/example_sitemap.py
```

**Website Crawling:**
```bash
docker-compose exec advertools python /app/scripts/example_crawl.py
```

**Keyword Generation:**
```bash
docker-compose exec advertools python /app/scripts/example_keywords.py
```

### 3. Interactive Python Shell

```bash
docker-compose exec advertools python -i crawler.py
```

Then run functions interactively:
```python
# Analyze sitemaps
run_sitemap_analysis(config)

# Crawl a website
run_crawler(config)
```

## Configuration

### Main Configuration File

Edit [`config/config.yaml`](config/config.yaml) to customize:

- **Sitemap settings**: URLs to analyze, recursion depth
- **Crawl settings**: Start URLs, depth limits, CSS/XPath selectors
- **API credentials**: SEM Rush, Google Ads, Twitter, YouTube
- **Export settings**: Output formats and compression

### Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your API keys and credentials

## Project Structure

```
.
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Python dependencies
├── crawler.py             # Main crawler script
├── config/
│   └── config.yaml        # Main configuration file
├── scripts/               # Example scripts
│   ├── example_sitemap.py
│   ├── example_crawl.py
│   └── example_keywords.py
├── data/                  # Input data (mounted volume)
├── output/                # Crawl outputs (mounted volume)
└── README.md
```

## Common Commands

### Access Container Shell
```bash
docker-compose exec advertools bash
```

### View Logs
```bash
docker-compose logs -f
```

### Stop Container
```bash
docker-compose down
```

### Rebuild After Changes
```bash
docker-compose up -d --build
```

## Usage Examples

### Sitemap Analysis

```python
import advertools as adv

sitemap_df = adv.sitemap_to_df("https://example.com/sitemap.xml")
sitemap_df.to_csv("/app/output/sitemap.csv", index=False)
```

### Website Crawling

```python
import advertools as adv

adv.crawl(
    url_list=["https://example.com"],
    output_file="/app/output/crawl.jl",
    follow_links=True,
    css_selectors=["h1", "h2", "title", "meta[name='description']"]
)
```

### Keyword Generation

```python
import advertools as adv

keywords = adv.kw_generate(
    products=["seo", "marketing"],
    words=["tools", "software"],
    match_types=["Exact", "Phrase"]
)
```

## API Integrations

Advertools supports various API integrations. Add your credentials to `.env` or `config.yaml`:

- **SEM Rush**: Competitor analysis, keyword research
- **Google Ads**: Campaign management, keyword planning
- **Twitter**: Social media analytics
- **YouTube**: Video analytics

## Output Files

All output files are saved to the `output/` directory:

- **JSON Lines (.jl)**: Default crawl output format
- **CSV**: Tabular data exports
- **Parquet**: Compressed columnar format

## Documentation

- [Advertools Documentation](https://advertools.readthedocs.io/)
- [Advertools GitHub](https://github.com/eliasdabbas/advertools)

## License

This Docker setup is provided as-is. Please refer to the [advertools license](https://github.com/eliasdabbas/advertools/blob/master/LICENSE) for the library itself.
