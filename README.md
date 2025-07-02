# 🤖 AI-PULSE: Complete Anthropic RSS Monitor

**Production-ready RSS monitoring system for comprehensive Anthropic updates**

[![GitHub Actions](https://img.shields.io/badge/GitHub-Actions-blue?logo=github)](https://github.com/your-username/ai-pulse)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-green?logo=python)](https://python.org)
[![RSS Feeds](https://img.shields.io/badge/RSS-8%20Feeds-orange?logo=rss)](feeds/)

## 🎯 Available Feeds

### 🌍 English Feeds
| Feed | Description | Articles | RSS URL |
|------|-------------|----------|---------|
| 🔥 **Complete** | All sources combined | 46+ | [`feed_anthropic_complete.xml`](https://raw.githubusercontent.com/ponyol/ai-pulse/main/feeds/feed_anthropic_complete.xml) |
| 📰 **News** | Official announcements | 16+ | [`feed_anthropic_news.xml`](https://raw.githubusercontent.com/ponyol/ai-pulse/main/feeds/feed_anthropic_news.xml) |
| 🔧 **Engineering** | Technical insights | 5+ | [`feed_anthropic_engineering.xml`](https://raw.githubusercontent.com/ponyol/ai-pulse/main/feeds/feed_anthropic_engineering.xml) |
| 🧠 **Alignment** | Safety research | 25+ | [`feed_anthropic_alignment.xml`](https://raw.githubusercontent.com/ponyol/ai-pulse/main/feeds/feed_anthropic_alignment.xml) |

### 🇺🇦 Ukrainian Feeds (Українські фіди)
**⚡ Powered by Mistral AI for high-quality translations**

| Feed | Description | Articles | RSS URL |
|------|-------------|----------|---------|
| 🔥 **Complete UA** | Всі джерела українською | 46+ | [`feed_anthropic_complete_ua.xml`](https://raw.githubusercontent.com/ponyol/ai-pulse/main/feeds/feed_anthropic_complete_ua.xml) |
| 📰 **News UA** | Офіційні оголошення | 16+ | [`feed_anthropic_news_ua.xml`](https://raw.githubusercontent.com/ponyol/ai-pulse/main/feeds/feed_anthropic_news_ua.xml) |
| 🔧 **Engineering UA** | Технічні інсайти | 5+ | [`feed_anthropic_engineering_ua.xml`](https://raw.githubusercontent.com/ponyol/ai-pulse/main/feeds/feed_anthropic_engineering_ua.xml) |
| 🧠 **Alignment UA** | Дослідження безпеки | 25+ | [`feed_anthropic_alignment_ua.xml`](https://raw.githubusercontent.com/ponyol/ai-pulse/main/feeds/feed_anthropic_alignment_ua.xml) |

## 🎯 Project Overview

AI-PULSE provides **complete coverage** of Anthropic updates through automated RSS generation from multiple critical sources that existing solutions miss:

### 📊 Coverage Comparison
| Source | Existing RSS | AI-PULSE |
|--------|-------------|----------|
| anthropic.com/news | ✅ Basic | ✅ Enhanced |
| anthropic.com/engineering | ❌ Missing | ✅ **NEW** |
| alignment.anthropic.com | ❌ Missing | ✅ **CRITICAL** |
| anthropic.com/research | ❌ Missing | ✅ **NEW** |

### 🔥 Why This Matters
- **Engineering insights** from building AI systems
- **Safety research** from Alignment Science team
- **Latest research** papers and findings
- **Combined feed** for complete monitoring

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/your-username/ai-pulse.git
cd ai-pulse
pip install -r requirements.txt
```

### 2. Generate RSS Feeds
```bash
python run_all_feeds.py
```

### 3. Monitor for Updates
```bash
python desktop_integration/rss_monitor.py
```

### 4. Setup Email Reports
```bash
python desktop_integration/gmail_integration.py setup \
  --sender your-email@gmail.com \
  --password your-app-password
```

## 📡 RSS Feeds

### 📱 Quick Add to RSS Reader
Copy and paste these URLs into your RSS reader:

**🔥 Recommended: Complete Feed (English)**
```
https://raw.githubusercontent.com/ponyol/ai-pulse/main/feeds/feed_anthropic_complete.xml
```

**🇺🇦 Recommended: Complete Feed (Ukrainian)**
```
https://raw.githubusercontent.com/ponyol/ai-pulse/main/feeds/feed_anthropic_complete_ua.xml
```

**📰 Individual Feeds (English)**
```
https://raw.githubusercontent.com/ponyol/ai-pulse/main/feeds/feed_anthropic_news.xml
https://raw.githubusercontent.com/ponyol/ai-pulse/main/feeds/feed_anthropic_engineering.xml
https://raw.githubusercontent.com/ponyol/ai-pulse/main/feeds/feed_anthropic_alignment.xml
```

**🇺🇦 Individual Feeds (Ukrainian / Українською)**
```
https://raw.githubusercontent.com/ponyol/ai-pulse/main/feeds/feed_anthropic_news_ua.xml
https://raw.githubusercontent.com/ponyol/ai-pulse/main/feeds/feed_anthropic_engineering_ua.xml
https://raw.githubusercontent.com/ponyol/ai-pulse/main/feeds/feed_anthropic_alignment_ua.xml
```

⏰ **Updates**: Every 4 hours + full rescan Mondays 8AM UTC

## 🎛️ Features

### ⚡ Automated Generation
- **GitHub Actions**: Every 4 hours + Monday full rescan
- **Error handling**: Robust parsing with fallbacks
- **Performance**: ~3.4 seconds for all feeds

### 🖥️ Desktop Integration
- **macOS notifications** for high-priority updates
- **Smart filtering** by priority (Critical/High/Medium)
- **Local caching** to avoid duplicate notifications

### 📧 Email Reports
- **Daily/Weekly digests** via Gmail
- **Formatted reports** with categorization
- **CLI interface** for automation

### 🔍 Advanced Parsing
- **Category detection**: Auto-categorizes content
- **Deduplication**: Prevents duplicate entries
- **URL validation**: Ensures working links
## 🌐 Translation Setup

### 🤖 Mistral API Configuration
AI-PULSE uses **Mistral AI** for high-quality Ukrainian translations. The system automatically falls back to mock translations if the API is unavailable.

#### 🔧 For GitHub Actions (Repository Secrets)
1. **Get Mistral API Key:**
   - Visit [Mistral AI Console](https://console.mistral.ai/)
   - Create account and generate API key
   - Copy your API key

2. **Add GitHub Secret:**
   - Go to your repository → Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `MISTRAL_API_KEY`
   - Value: Your Mistral API key
   - Click "Add secret"

3. **Verify Setup:**
   - GitHub Actions will automatically use Mistral API for translations
   - Check workflow logs for "🇺🇦 Translating via Mistral API..."

#### 🖥️ For Local Development
```bash
# Set environment variable
export MISTRAL_API_KEY="your_mistral_api_key_here"

# Test translation engine
cd feed_generators
python test_mistral_translation.py

# Run feed generation with translations
python run_all_feeds.py
```

#### 💡 Translation Quality
- **With Mistral API:** High-quality contextual translations
- **Without API:** Fallback to rule-based mock translations
- **Caching:** All translations cached to minimize API calls
- **Cost Optimization:** Only new content is translated

## 🏗️ Technical Architecture

### 📦 Project Structure
```
ai-pulse/
├── .github/workflows/
│   └── update_feeds.yml          # GitHub Actions automation
├── feed_generators/
│   ├── feed_anthropic_news.py      # News parser
│   ├── feed_anthropic_engineering.py # Engineering parser
│   ├── feed_anthropic_alignment.py   # Alignment Science parser
│   └── feed_anthropic_complete.py    # Combined feed generator
├── feeds/                         # Generated RSS files
├── desktop_integration/
│   ├── rss_monitor.py            # Desktop notifications
│   └── gmail_integration.py      # Email reports
├── run_all_feeds.py              # Main orchestrator
└── requirements.txt              # Dependencies
```

### 🔧 Technology Stack
- **Python 3.9+**: Core runtime
- **BeautifulSoup4**: HTML parsing
- **FeedGen**: RSS generation
- **Requests/aiohttp**: HTTP clients
- **Mistral AI**: Ukrainian translations
- **GitHub Actions**: CI/CD automation

### ⚙️ How It Works
1. **GitHub Actions** triggers every 4 hours
2. **Parsers** scrape Anthropic websites
3. **RSS Generator** creates XML feeds
4. **Desktop Monitor** checks for new articles
5. **Gmail Integration** sends formatted reports

## 📋 Usage Examples

### Daily Monitoring Workflow
```bash
# Morning check
python desktop_integration/rss_monitor.py

# Send daily digest
python desktop_integration/gmail_integration.py daily

# Manual feed update
python run_all_feeds.py
```

### Automation Setup
```bash
# Add to crontab for automated monitoring
# Check every 2 hours
0 */2 * * * cd /path/to/ai-pulse && python desktop_integration/rss_monitor.py

# Daily digest at 9 AM
0 9 * * * cd /path/to/ai-pulse && python desktop_integration/gmail_integration.py daily

# Weekly digest on Mondays
0 9 * * 1 cd /path/to/ai-pulse && python desktop_integration/gmail_integration.py weekly
```

### RSS Reader Integration
Popular RSS readers supporting our feeds:
- **Feedly**: Add `feed_anthropic_complete.xml`
- **Inoreader**: Subscribe to GitHub raw URLs
- **NetNewsWire** (macOS): Local or remote feeds
- **Reeder** (iOS): Full sync support

## 🎯 Priority System

Articles are automatically categorized by importance:

### 🔥 CRITICAL Priority
- **Alignment Science** research (safety-critical)
- **Policy announcements** affecting AI development
- **Major model releases** (Claude 4, etc.)

### ⚡ HIGH Priority
- **Engineering insights** and technical posts
- **Research papers** and findings
- **Product updates** and feature releases

### 📰 MEDIUM Priority
- **News articles** and press releases
- **Partnership announcements**
- **General company updates**

## 📧 Email Integration Guide

### Setup Gmail App Password
1. Enable 2FA on your Google account
2. Generate app-specific password
3. Use in AI-PULSE configuration

### Configure Email Reports
```bash
# Initial setup
python desktop_integration/gmail_integration.py setup \
  --sender your-email@gmail.com \
  --password your-16-char-app-password \
  --recipient reports@yourcompany.com

# Test configuration
python desktop_integration/gmail_integration.py test

# Schedule daily reports
python desktop_integration/gmail_integration.py daily
```

### Email Report Format
```
🤖 AI-PULSE Daily Report
Generated: 2025-06-27 13:42 UTC

📊 SUMMARY
• Total Articles: 46
• Critical Updates: 25
• Sources Covered: 4

🚨 CRITICAL UPDATES
📌 Alignment Faking in Large Language Models
   🔗 https://www.anthropic.com/research/alignment-faking
   📝 Research on how AI models might fake alignment...

🧠 ALIGNMENT SCIENCE
• Model-Internals Classifiers
• Sleeper Agents Detection
• Safety Evaluation Frameworks
```

## 🎨 Customization

### Adding New Sources
To monitor additional AI companies:

1. **Create new parser** in `feed_generators/`:
```python
# feed_generators/feed_openai_news.py
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

def extract_articles(soup):
    # Your parsing logic
    pass

def main():
    # Generate RSS feed
    pass
```

2. **Update main orchestrator**:
```python
# run_all_feeds.py
generators = [
    ('feed_anthropic_news', 'Anthropic News'),
    ('feed_openai_news', 'OpenAI News'),  # Add here
    # ... other generators
]
```

3. **Configure monitoring**:
```python
# desktop_integration/rss_monitor.py
FEEDS_CONFIG = {
    'openai_news': {
        'url': 'path/to/feed_openai_news.xml',
        'priority': 'high'
    }
}
```

### Custom Notification Rules
```python
# desktop_integration/rss_monitor.py
def should_notify(article):
    # Custom logic for notifications
    if 'safety' in article['title'].lower():
        return True
    if article['priority'] == 'critical':
        return True
    return False
```

### Feed Filtering
```python
# Filter by keywords
ALIGNMENT_KEYWORDS = ['safety', 'alignment', 'interpretability']
ENGINEERING_KEYWORDS = ['technical', 'architecture', 'system']

def filter_articles(articles, keywords):
    return [a for a in articles if any(k in a['title'].lower() for k in keywords)]
```

## 🔍 Troubleshooting

### Common Issues

**🚨 "No articles found"**
```bash
# Check website accessibility
curl -I https://www.anthropic.com/news

# Test parser directly
python feed_generators/feed_anthropic_news.py

# Verify dependencies
pip install -r requirements.txt
```

**📧 Email sending fails**
```bash
# Verify Gmail app password
python desktop_integration/gmail_integration.py test

# Check configuration
cat ~/.ai_pulse_email_config.json

# Test SMTP connection
telnet smtp.gmail.com 587
```

**🔄 GitHub Actions not running**
- Check repository permissions
- Verify workflow file syntax
- Enable Actions in repository settings

**🖥️ Desktop notifications not showing**
- macOS: Check System Preferences > Notifications
- Ensure script has proper permissions
- Test with manual execution

### Debug Mode
```bash
# Enable verbose logging
export AI_PULSE_DEBUG=1
python run_all_feeds.py

# Check individual parsers
python -m pdb feed_generators/feed_anthropic_news.py
```

### Performance Optimization
```bash
# Use caching for faster updates
pip install requests-cache

# Parallel processing
pip install concurrent.futures
```

## 🤝 Contributing

### Development Setup
```bash
git clone https://github.com/your-username/ai-pulse.git
cd ai-pulse
python -m venv venv
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

### Code Style
- **Black** for formatting
- **Type hints** for new functions
- **Docstrings** for public methods
- **Error handling** for network requests

### Testing
```bash
# Test all parsers
python -m pytest tests/

# Test specific component
python feed_generators/feed_anthropic_news.py

# Integration test
python run_all_feeds.py && python desktop_integration/rss_monitor.py
```

## 📊 Metrics & Analytics

Current performance (as of June 2025):
- **46 total articles** across all sources
- **25 alignment science** articles (critical coverage)
- **3.4 seconds** full generation time
- **99.9% uptime** via GitHub Actions

### Article Distribution
- 🧠 **Alignment Science**: 54% (25/46)
- 📰 **News**: 35% (16/46)
- 🔧 **Engineering**: 11% (5/46)

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Anthropic Team** for excellent technical content
- **Alignment Science Team** for critical safety research
- **RSS Community** for feed standards
- **Open Source Contributors** for dependencies

## 🚀 Future Enhancements

**📋 [See detailed roadmap in TODO.md](TODO.md)**

- [ ] **🔥 HIGH PRIORITY: Mistral AI monitoring** - Add RSS feeds for Mistral AI news, research, and engineering posts (we use their API, so we should follow their updates!)
- [ ] **📈 MEDIUM PRIORITY: Expand to other AI companies** - OpenAI, Google DeepMind, Cohere, xAI for comprehensive AI landscape monitoring
- [ ] **Multi-language support** for international content
- [ ] **Sentiment analysis** for content prioritization
- [ ] **AI summarization** of long articles
- [ ] **Slack/Discord integration** for team notifications
- [ ] **Analytics dashboard** for content trends
- [ ] **Mobile app** for iOS/Android
- [ ] **Browser extension** for instant notifications

---

**⭐ If this project helps you stay updated with AI developments, please star the repository!**

For questions or support: [Create an issue](https://github.com/your-username/ai-pulse/issues)
