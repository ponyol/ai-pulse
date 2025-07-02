# AI-PULSE Project Structure

## Directory Layout
```
ai-pulse/
├── .github/workflows/           # CI/CD automation
│   └── update_feeds.yml        # GitHub Actions workflow
├── feed_generators/            # RSS generation modules
│   ├── feed_anthropic_news.py      # News parser (16+ articles)
│   ├── feed_anthropic_engineering.py # Engineering blog (5+ articles)
│   ├── feed_anthropic_alignment.py   # Alignment Science (25+ articles)
│   └── feed_anthropic_complete.py    # Combined feed (46+ articles)
├── feeds/                      # Generated RSS XML files
│   ├── feed_anthropic_complete.xml   # Main combined feed
│   ├── feed_anthropic_news.xml       # News-only feed
│   ├── feed_anthropic_engineering.xml # Engineering-only feed
│   └── feed_anthropic_alignment.xml  # Alignment-only feed
├── desktop_integration/        # Local monitoring tools
│   ├── rss_monitor.py          # Desktop notifications & caching
│   └── gmail_integration.py    # Email reports & CLI
├── .serena/                    # Serena project config
│   ├── project.yml             # Project settings
│   └── memories/               # Onboarding memories
├── run_all_feeds.py           # Main orchestrator
├── requirements.txt           # Python dependencies
├── README.md                  # Comprehensive documentation
├── LICENSE                    # MIT license
└── .gitignore                # Git exclusions
```

## Component Architecture

### **Feed Generators** (`feed_generators/`)
Each parser follows consistent architecture:

#### **Common Structure**
- **Constants**: `BASE_URL`, `*_URL`, `OUTPUT_FILE`, `USER_AGENT`
- **Functions**: `get_page_content()`, `extract_articles()`, `extract_single_article()`, `generate_rss_feed()`, `main()`
- **Error Handling**: Try/catch with graceful degradation
- **Logging**: Emoji-enhanced progress indicators

#### **Specific Parsers**
- **News**: `anthropic.com/news` - Official announcements, policy, product updates
- **Engineering**: `anthropic.com/engineering` - Technical insights, system architecture
- **Alignment**: `alignment.anthropic.com` - Safety research, alignment science
- **Complete**: Aggregates all sources into single comprehensive feed

### **Desktop Integration** (`desktop_integration/`)

#### **RSS Monitor** (`rss_monitor.py`)
- **Class**: `RSSMonitor` - Main monitoring logic
- **Features**: macOS notifications, caching, priority filtering
- **Config**: `FEEDS_CONFIG` with URL and priority mappings
- **Cache**: `~/.ai_pulse_cache.json` for deduplication

#### **Gmail Integration** (`gmail_integration.py`)
- **Class**: `GmailIntegration` - Email functionality
- **Features**: Daily/weekly digests, SMTP configuration, CLI interface
- **Config**: `~/.ai_pulse_email_config.json` for credentials
- **Reports**: HTML-formatted email reports with categorization

### **Automation** (`.github/workflows/`)

#### **GitHub Actions** (`update_feeds.yml`)
- **Triggers**: Every 4 hours, Monday full rescan, manual, code changes
- **Environment**: Ubuntu Latest, Python 3.11
- **Permissions**: `contents: write`, `actions: read`
- **Steps**: Checkout → Setup → Install → Generate → Commit → Artifact
- **Optimization**: pip caching, feed size reporting

## Data Flow Architecture

### **RSS Generation Pipeline**
1. **Trigger**: GitHub Actions cron or manual execution
2. **Orchestration**: `run_all_feeds.py` imports and executes parsers
3. **Web Scraping**: Individual parsers fetch HTML content
4. **Content Extraction**: BeautifulSoup parsing into structured data
5. **RSS Generation**: feedgen converts to XML format
6. **File Output**: XML files written to `feeds/` directory
7. **Git Commit**: Automated commit and push via GitHub Actions

### **Desktop Monitoring Pipeline**
1. **RSS Parsing**: Monitor reads generated XML feeds
2. **Cache Comparison**: Check against `~/.ai_pulse_cache.json`
3. **Priority Filtering**: Categorize by importance (Critical/High/Medium)
4. **Notification**: macOS system notifications for new articles
5. **Cache Update**: Store processed articles to prevent duplicates

### **Email Integration Pipeline**
1. **Article Collection**: Aggregate from multiple RSS feeds
2. **Categorization**: Group by source and priority
3. **HTML Generation**: Format into readable email report
4. **SMTP Delivery**: Send via Gmail SMTP with app password
5. **Scheduling**: Cron integration for daily/weekly automation

## Configuration Management

### **Runtime Configuration**
- **Feed URLs**: Hardcoded in parser constants
- **Output Paths**: Relative to project root (`feeds/`)
- **Timeouts**: Embedded in request calls
- **User Agent**: Descriptive, non-intrusive

### **User Configuration**
- **Email Settings**: `~/.ai_pulse_email_config.json`
- **Monitor Cache**: `~/.ai_pulse_cache.json`
- **Environment Variables**: `AI_PULSE_DEBUG` for verbose logging

### **GitHub Configuration**
- **Secrets**: None required (public RSS generation)
- **Permissions**: Repository write access for automated commits
- **Workflow**: Schedule, manual trigger, push-based updates

## Extensibility Design

### **Adding New Sources**
1. **Create Parser**: `feed_generators/feed_[company]_[type].py`
2. **Update Orchestrator**: Add to `generators` list in `run_all_feeds.py`
3. **Configure Monitoring**: Add to `FEEDS_CONFIG` in `rss_monitor.py`
4. **Update Documentation**: Add to README feeds table

### **Platform Expansion**
- **Linux Support**: Replace macOS-specific notification calls
- **Windows Support**: Adapt notification and cron systems
- **Cloud Deployment**: Containerize with Docker, deploy on Kubernetes
- **Mobile Integration**: API layer for iOS/Android applications

### **Integration Points**
- **Slack/Discord**: Webhook integration for team notifications
- **Analytics**: Database storage for content trend analysis
- **AI Enhancement**: Content summarization and sentiment analysis
- **Multi-format**: JSON API layer alongside RSS output
