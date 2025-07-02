# AI-PULSE Suggested Commands

## Essential Development Commands

### **Project Setup**
```bash
# Clone and setup
git clone https://github.com/ponyol/ai-pulse.git
cd ai-pulse
python -m venv venv
source venv/bin/activate  # macOS activation
pip install -r requirements.txt
```

### **Core Operations**
```bash
# Generate all RSS feeds
python run_all_feeds.py

# Test individual parsers
python feed_generators/feed_anthropic_news.py
python feed_generators/feed_anthropic_engineering.py
python feed_generators/feed_anthropic_alignment.py
python feed_generators/feed_anthropic_complete.py

# Monitor for updates
python desktop_integration/rss_monitor.py

# Email integration setup
python desktop_integration/gmail_integration.py setup \
  --sender your-email@gmail.com \
  --password your-app-password
```

## Testing & Quality Assurance

### **Manual Testing**
```bash
# Test all feed generators
python run_all_feeds.py

# Verify feed generation
ls -la feeds/
du -h feeds/*

# Test desktop notifications
python desktop_integration/rss_monitor.py

# Test email functionality
python desktop_integration/gmail_integration.py test
python desktop_integration/gmail_integration.py daily
```

### **Debug Mode**
```bash
# Enable verbose logging
export AI_PULSE_DEBUG=1
python run_all_feeds.py

# Debug specific parsers
python -m pdb feed_generators/feed_anthropic_news.py
```

### **Network Testing**
```bash
# Test website accessibility
curl -I https://www.anthropic.com/news
curl -I https://www.anthropic.com/engineering
curl -I https://alignment.anthropic.com

# Test RSS feed validity
curl -s https://raw.githubusercontent.com/ponyol/ai-pulse/main/feeds/feed_anthropic_complete.xml | head -20
```

## Automation & Monitoring

### **Cron Integration (macOS)**
```bash
# Edit crontab
crontab -e

# Monitor every 2 hours
0 */2 * * * cd /path/to/ai-pulse && python desktop_integration/rss_monitor.py

# Daily digest at 9 AM
0 9 * * * cd /path/to/ai-pulse && python desktop_integration/gmail_integration.py daily

# Weekly digest on Mondays
0 9 * * 1 cd /path/to/ai-pulse && python desktop_integration/gmail_integration.py weekly
```

### **GitHub Actions**
```bash
# Manually trigger workflow
gh workflow run update_feeds.yml

# Check workflow status
gh run list --workflow=update_feeds.yml

# View workflow logs
gh run view --log
```

## System Utils (Darwin/macOS)

### **File Operations**
```bash
# List files with details
ls -la feeds/

# Find Python files
find . -name "*.py" -type f

# Search for patterns in code
grep -r "anthropic.com" feed_generators/

# File sizes
du -h feeds/*
du -sh .  # Total project size
```

### **Process Management**
```bash
# Check running Python processes
ps aux | grep python

# Kill stuck processes
pkill -f "python.*ai-pulse"

# Monitor system resources
top -o cpu  # CPU usage
top -o mem  # Memory usage
```

### **Network & Connectivity**
```bash
# Test SMTP connection (Gmail)
telnet smtp.gmail.com 587

# Check DNS resolution
nslookup anthropic.com

# Test HTTP response times
time curl -s -o /dev/null https://www.anthropic.com/news
```

## Development Workflow

### **Code Quality**
```bash
# Format code (recommended)
black feed_generators/ desktop_integration/ *.py

# Type checking (optional)
mypy feed_generators/

# Import sorting (optional)
isort feed_generators/ desktop_integration/
```

### **Git Operations**
```bash
# Standard workflow
git add .
git commit -m "🔧 Feature: description"
git push origin main

# Check repository status
git status
git log --oneline -10

# Create feature branch
git checkout -b feature/new-source
```

### **Dependency Management**
```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Add new dependency
pip install new-package
pip freeze > requirements.txt

# Check for security issues
pip audit
```

## Troubleshooting Commands

### **Common Issues**
```bash
# Permission issues
chmod +x run_all_feeds.py
chmod +x desktop_integration/*.py

# Clean Python cache
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete

# Reset virtual environment
deactivate
rm -rf venv/
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **Performance Analysis**
```bash
# Time operations
time python run_all_feeds.py

# Memory usage
python -m memory_profiler run_all_feeds.py

# Profile code execution
python -m cProfile run_all_feeds.py
```

## Deployment & Production

### **Repository Management**
```bash
# Verify feeds are updated
git log --oneline feeds/

# Check GitHub Actions status
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/ponyol/ai-pulse/actions/runs

# Monitor feed accessibility
curl -I https://raw.githubusercontent.com/ponyol/ai-pulse/main/feeds/feed_anthropic_complete.xml
```

### **Monitoring & Alerts**
```bash
# Check feed freshness
stat feeds/feed_anthropic_complete.xml

# Validate RSS format
xmllint --noout feeds/feed_anthropic_complete.xml

# Count articles
grep -c "<item>" feeds/feed_anthropic_complete.xml
```
