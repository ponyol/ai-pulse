# AI-PULSE Task Completion Guidelines

## After Code Changes

### **1. Testing Requirements**
```bash
# MANDATORY: Test all feed generators
python run_all_feeds.py

# Verify feeds generated successfully
ls -la feeds/
du -h feeds/*

# Test individual components if modified
python feed_generators/feed_anthropic_news.py      # If news parser changed
python feed_generators/feed_anthropic_engineering.py # If engineering parser changed
python feed_generators/feed_anthropic_alignment.py   # If alignment parser changed
python feed_generators/feed_anthropic_complete.py    # If combined feed changed
```

### **2. Quality Assurance**
```bash
# Validate RSS XML format
xmllint --noout feeds/feed_anthropic_complete.xml
xmllint --noout feeds/feed_anthropic_news.xml

# Count articles to verify content
grep -c "<item>" feeds/feed_anthropic_complete.xml
grep -c "<item>" feeds/feed_anthropic_news.xml

# Test desktop integration if modified
python desktop_integration/rss_monitor.py

# Test email functionality if modified
python desktop_integration/gmail_integration.py test
```

### **3. Performance Verification**
```bash
# Measure generation time (should be ~3.4 seconds)
time python run_all_feeds.py

# Check feed sizes (reasonable content)
du -h feeds/*

# Verify no memory leaks or excessive resource usage
top -p $(pgrep -f "python.*ai-pulse")
```

## Git Workflow

### **4. Commit Process**
```bash
# Stage changes
git add .

# Commit with descriptive message and emoji
git commit -m "🔧 Fix: description of changes"
# OR
git commit -m "✨ Feature: description of new functionality"
# OR
git commit -m "🐛 Bug fix: description of issue resolved"

# Push to main branch
git push origin main
```

### **5. GitHub Actions Verification**
```bash
# Wait for GitHub Actions to complete
gh run list --workflow=update_feeds.yml

# Check for any workflow failures
gh run view --log

# Verify automated feed updates work correctly
curl -I https://raw.githubusercontent.com/ponyol/ai-pulse/main/feeds/feed_anthropic_complete.xml
```

## Code Quality Standards

### **6. Pre-commit Checks** (Recommended)
```bash
# Format code
black feed_generators/ desktop_integration/ *.py

# Sort imports
isort feed_generators/ desktop_integration/

# Type checking (if using mypy)
mypy feed_generators/ desktop_integration/

# Remove unused imports
autoflake --remove-all-unused-imports --in-place feed_generators/*.py desktop_integration/*.py
```

### **7. Documentation Updates**
- **README.md**: Update if new features or major changes
- **Docstrings**: Ensure all new functions have proper documentation
- **Comments**: Add inline comments for complex parsing logic
- **Memory Files**: Update Serena memories if architecture changes

## Deployment Verification

### **8. Production Readiness**
```bash
# Verify RSS feeds are publicly accessible
curl -s https://raw.githubusercontent.com/ponyol/ai-pulse/main/feeds/feed_anthropic_complete.xml | head -20

# Test RSS feed validity in readers
# Add to Feedly/Inoreader to verify proper parsing

# Check GitHub Actions automation
# Ensure scheduled runs work correctly at 4-hour intervals
```

### **9. Monitoring Setup**
```bash
# For new installations, set up cron monitoring
crontab -e
# Add lines for automated monitoring and email reports

# Test email integration setup
python desktop_integration/gmail_integration.py setup
python desktop_integration/gmail_integration.py daily

# Verify macOS notifications work
python desktop_integration/rss_monitor.py
```

## Error Handling

### **10. Common Issues Resolution**
```bash
# If feeds not generating:
export AI_PULSE_DEBUG=1
python run_all_feeds.py

# If network errors:
curl -I https://www.anthropic.com/news
curl -I https://www.anthropic.com/engineering
curl -I https://alignment.anthropic.com

# If email not working:
python desktop_integration/gmail_integration.py test
# Check Gmail app password configuration
```

### **11. Rollback Procedure**
```bash
# If deployment breaks production:
git log --oneline -10  # Find last working commit
git revert HEAD        # Revert last commit
git push origin main   # Deploy fix

# Emergency: Force reset (use carefully)
git reset --hard HEAD~1
git push --force-with-lease origin main
```

## Success Criteria

### **12. Task Completion Checklist**
- [ ] All tests pass (`python run_all_feeds.py` succeeds)
- [ ] RSS feeds validate (xmllint passes)
- [ ] Article counts are reasonable (>40 total articles)
- [ ] Performance is acceptable (<5 seconds generation)
- [ ] GitHub Actions complete successfully
- [ ] No regression in existing functionality
- [ ] Code follows project style conventions
- [ ] Documentation updated if necessary
- [ ] RSS feeds accessible via GitHub raw URLs

### **13. Long-term Maintenance**
- **Weekly**: Check GitHub Actions success rate
- **Monthly**: Verify article counts and content quality
- **Quarterly**: Update dependencies in requirements.txt
- **As needed**: Adapt parsers if website structures change

## Emergency Contacts

### **14. Escalation Path**
- **Repository Issues**: Create GitHub issue with error logs
- **External Dependencies**: Check BeautifulSoup/feedgen documentation
- **Anthropic Website Changes**: Analyze new HTML structure, adapt parsers
- **GitHub Actions Problems**: Check GitHub Status page, review workflow syntax

Remember: **Quality over speed** - always verify functionality before considering a task complete.
