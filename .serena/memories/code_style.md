# AI-PULSE Code Style & Conventions

## Naming Conventions

### **Variables & Functions**
- **snake_case** for all variables and functions
- **UPPER_CASE** for module-level constants
- **Descriptive names**: `extract_articles()`, `generate_rss_feed()`
- **Boolean prefixes**: `should_notify()`, `is_valid()`

### **Constants**
```python
BASE_URL = "https://www.anthropic.com"
NEWS_URL = f"{BASE_URL}/news"
OUTPUT_FILE = "feeds/feed_anthropic_news.xml"
USER_AGENT = "AI-PULSE RSS Monitor 1.0"
```

### **File Naming**
- **feed_generators/**: `feed_[source]_[type].py`
- **desktop_integration/**: `[function]_integration.py`
- **Main scripts**: `run_all_feeds.py`

## Function Design

### **Type Hints**
```python
def extract_articles(soup: BeautifulSoup) -> list:
    """Extract article information from the news page"""
    
def get_page_content(url: str) -> BeautifulSoup:
    """Fetch and parse web page content"""
```

### **Docstrings**
- **Required** for all public functions
- **Google style** preferred
- **Brief description** in first line
- **Return types** documented

```python
def extract_single_article(element) -> dict:
    """Extract single article data from HTML element
    
    Args:
        element: BeautifulSoup element containing article data
        
    Returns:
        dict: Article data with title, url, date, description
    """
```

### **Error Handling**
```python
try:
    article = extract_single_article(element)
    if article:
        articles.append(article)
except Exception as e:
    logger.debug(f"Error processing article element: {e}")
    continue
```

## Logging Standards

### **Logger Setup**
```python
import logging
logger = logging.getLogger(__name__)
```

### **Log Levels & Emojis**
- **INFO**: `🚀`, `📰`, `✅`, `🎉` for progress and success
- **ERROR**: `❌`, `🚨` for failures
- **WARNING**: `⚠️` for partial failures
- **DEBUG**: Technical details, no emojis

```python
logger.info("🚀 AI-PULSE RSS generation started")
logger.info("📰 Generating: Anthropic News")
logger.info("✅ Anthropic News - Success")
logger.error("❌ Failed to parse article")
```

## Project Structure Conventions

### **Directory Organization**
```
ai-pulse/
├── feed_generators/          # Source-specific parsers
├── feeds/                    # Generated RSS XML files
├── desktop_integration/      # Local monitoring tools
├── .github/workflows/       # CI/CD automation
├── run_all_feeds.py        # Main orchestrator
└── requirements.txt        # Dependencies
```

### **Import Order**
1. **Standard library**: `import sys, logging, datetime`
2. **Third-party**: `import requests, feedgen`
3. **Local modules**: `from feed_generators import utils`

## Configuration Management

### **Constants at Module Level**
```python
# Configuration constants at top of file
BASE_URL = "https://www.anthropic.com"
OUTPUT_FILE = "feeds/feed_anthropic_news.xml"
CHECK_INTERVAL_HOURS = 2
```

### **JSON Configuration Files**
```python
CONFIG_FILE = Path.home() / '.ai_pulse_email_config.json'
CACHE_FILE = Path.home() / '.ai_pulse_cache.json'
```

## Performance Standards

### **Network Operations**
- **Timeout handling**: All requests with timeouts
- **User-Agent**: Descriptive, non-intrusive
- **Rate limiting**: Respectful scraping practices
- **Caching**: Optional for development

### **Memory Management**
- **Limited processing**: `[:50]` to avoid memory issues
- **Generator patterns**: For large data sets
- **Early returns**: Exit on error conditions

## Git Workflow

### **Commit Messages**
- **Emoji prefixes**: `🤖` for automation, `🐛` for fixes
- **Descriptive**: `"🤖 Update RSS feeds - 2025-06-27 13:42 UTC"`
- **Component scope**: `"🔧 Fix GitHub Actions permissions"`

### **Branch Protection**
- **main**: Production-ready code only
- **Actions permissions**: `contents: write`, `actions: read`
- **Automated commits**: Via `git-auto-commit-action`
