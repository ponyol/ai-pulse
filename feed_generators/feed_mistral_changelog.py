#!/usr/bin/env python3
"""
Mistral AI Changelog RSS Feed Generator
Parses docs.mistral.ai/changelog and generates RSS feed

This module scrapes the Mistral AI API changelog page and extracts:
- API updates and changes
- New model releases
- Feature announcements
- Deprecation notices
- Version information

Author: AI-PULSE Project
"""

import requests
import logging
from datetime import datetime, timezone
from pathlib import Path
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from urllib.parse import urljoin, urlparse
import re

# Setup logging
logger = logging.getLogger('mistral-changelog')

# Configuration
BASE_URL = "https://docs.mistral.ai"
CHANGELOG_URL = f"{BASE_URL}/getting-started/changelog"
OUTPUT_FILE = "feeds/feed_mistral_changelog.xml"
USER_AGENT = "AI-PULSE RSS Generator 1.0 (github.com/ponyol/ai-pulse)"

def get_page_content(url: str) -> BeautifulSoup:
    """Fetch and parse webpage content"""
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        logger.info(f"✅ Successfully fetched: {url}")
        return BeautifulSoup(response.content, 'html.parser')
    except requests.RequestException as e:
        logger.error(f"❌ Failed to fetch {url}: {e}")
        raise

def extract_changelog_entries(soup: BeautifulSoup) -> list:
    """Extract changelog entries from the documentation page"""
    entries = []
    seen_titles = set()
    
    # Pattern 1: Look for date headers (common in changelogs)
    date_headers = soup.find_all(['h1', 'h2', 'h3', 'h4'], string=re.compile(r'.*20\d{2}.*'))
    
    for header in date_headers:
        try:
            entry = extract_changelog_section(header)
            if entry and entry['title'] not in seen_titles:
                entries.append(entry)
                seen_titles.add(entry['title'])
        except Exception as e:
            logger.debug(f"Error processing date header: {e}")
    
    # Pattern 2: Look for list items with dates
    date_items = soup.find_all(['li', 'div', 'p'], string=re.compile(r'.*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).*20\d{2}.*'))
    
    for item in date_items:
        try:
            entry = extract_changelog_item(item)
            if entry and entry['title'] not in seen_titles:
                entries.append(entry)
                seen_titles.add(entry['title'])
        except Exception as e:
            logger.debug(f"Error processing date item: {e}")
    
    # Pattern 3: Look for specific changelog patterns
    changelog_sections = soup.find_all(['div', 'section'], class_=re.compile(r'.*(changelog|release|update).*', re.I))
    
    for section in changelog_sections:
        try:
            sub_entries = extract_section_entries(section)
            for entry in sub_entries:
                if entry and entry['title'] not in seen_titles:
                    entries.append(entry)
                    seen_titles.add(entry['title'])
        except Exception as e:
            logger.debug(f"Error processing changelog section: {e}")
    
    # Pattern 4: Look for strong/bold text that might indicate updates
    strong_elements = soup.find_all(['strong', 'b'], string=re.compile(r'.*(release|update|new|deprecat|fix).*', re.I))
    
    for element in strong_elements:
        try:
            entry = extract_from_strong_element(element)
            if entry and entry['title'] not in seen_titles:
                entries.append(entry)
                seen_titles.add(entry['title'])
        except Exception as e:
            logger.debug(f"Error processing strong element: {e}")
    
    logger.info(f"📰 Extracted {len(entries)} unique changelog entries")
    return entries

def extract_changelog_section(header) -> dict:
    """Extract changelog entry from a date header section"""
    date_text = header.get_text(strip=True)
    
    # Find the content following this header
    content_elements = []
    current = header.next_sibling
    
    while current and not (current.name in ['h1', 'h2', 'h3', 'h4'] and 
                          re.search(r'.*20\d{2}.*', current.get_text() if hasattr(current, 'get_text') else '')):
        if hasattr(current, 'name') and current.name:
            content_elements.append(current)
        current = current.next_sibling
        if len(content_elements) > 20:  # Prevent infinite loops
            break
    
    # Extract content
    content_text = ""
    updates = []
    
    for elem in content_elements:
        if hasattr(elem, 'get_text'):
            text = elem.get_text(strip=True)
            if text:
                content_text += text + "\n"
                # Look for specific updates
                if any(keyword in text.lower() for keyword in ['released', 'new', 'added', 'fixed', 'deprecated']):
                    updates.append(text)
    
    if not content_text.strip():
        return None
    
    return {
        'title': f"API Update - {date_text}",
        'date': parse_date(date_text),
        'description': content_text.strip()[:500] + "..." if len(content_text) > 500 else content_text.strip(),
        'url': f"{CHANGELOG_URL}#{create_anchor(date_text)}",
        'category': 'API Update',
        'updates': updates
    }

def extract_changelog_item(item) -> dict:
    """Extract changelog entry from a list item or paragraph"""
    text = item.get_text(strip=True)
    
    # Extract date from text
    date_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{1,2},?\s+20\d{2}', text)
    if not date_match:
        date_match = re.search(r'20\d{2}-\d{2}-\d{2}', text)
    
    if not date_match:
        return None
    
    date_str = date_match.group(0)
    
    # Determine update type and title
    update_type = 'Update'
    if 'release' in text.lower():
        update_type = 'Release'
    elif 'deprecat' in text.lower():
        update_type = 'Deprecation'
    elif 'fix' in text.lower():
        update_type = 'Fix'
    elif 'new' in text.lower():
        update_type = 'New Feature'
    
    # Create title
    title_text = text.replace(date_str, '').strip()
    if len(title_text) > 100:
        title_text = title_text[:100] + "..."
    
    title = f"{update_type} - {title_text}" if title_text else f"{update_type} - {date_str}"
    
    return {
        'title': title,
        'date': parse_date(date_str),
        'description': text,
        'url': f"{CHANGELOG_URL}#{create_anchor(title)}",
        'category': update_type
    }

def extract_section_entries(section) -> list:
    """Extract multiple entries from a changelog section"""
    entries = []
    
    # Look for individual update items within this section
    items = section.find_all(['li', 'p', 'div'], string=re.compile(r'.*(release|update|new|fix|deprecat).*', re.I))
    
    for item in items:
        text = item.get_text(strip=True)
        if len(text) < 20:  # Skip very short items
            continue
            
        # Try to find dates
        date_match = re.search(r'20\d{2}-\d{2}-\d{2}', text)
        date = parse_date(date_match.group(0)) if date_match else datetime.now(timezone.utc)
        
        entry = {
            'title': text[:100] + "..." if len(text) > 100 else text,
            'date': date,
            'description': text,
            'url': f"{CHANGELOG_URL}#{create_anchor(text)}",
            'category': 'API Change'
        }
        entries.append(entry)
    
    return entries

def extract_from_strong_element(element) -> dict:
    """Extract changelog entry from a strong/bold element"""
    text = element.get_text(strip=True)
    
    # Get surrounding context
    parent = element.parent
    if parent:
        context = parent.get_text(strip=True)
    else:
        context = text
    
    # Try to find date in context
    date_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{1,2},?\s+20\d{2}', context)
    if not date_match:
        date_match = re.search(r'20\d{2}-\d{2}-\d{2}', context)
    
    date = parse_date(date_match.group(0)) if date_match else datetime.now(timezone.utc)
    
    return {
        'title': f"Update: {text}",
        'date': date,
        'description': context,
        'url': f"{CHANGELOG_URL}#{create_anchor(text)}",
        'category': 'Feature Update'
    }

def create_anchor(text: str) -> str:
    """Create URL anchor from text"""
    return re.sub(r'[^a-zA-Z0-9]+', '-', text.lower()).strip('-')

def parse_date(date_str: str) -> datetime:
    """Parse various date formats"""
    if not date_str:
        return datetime.now(timezone.utc)
    
    # Common date formats for changelog
    formats = [
        '%Y-%m-%d',
        '%b %d, %Y',
        '%B %d, %Y',
        '%b. %d, %Y',
        '%B. %d, %Y',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%SZ'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    
    # Try to extract just year and month
    year_month_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+20\d{2}', date_str)
    if year_month_match:
        try:
            return datetime.strptime(year_month_match.group(0), '%b %Y').replace(tzinfo=timezone.utc)
        except:
            pass
    
    return datetime.now(timezone.utc)

def create_rss_feed(entries: list) -> None:
    """Create RSS feed from changelog entries"""
    if not entries:
        logger.warning("No changelog entries found, creating empty feed")
    
    # Create feed
    fg = FeedGenerator()
    fg.id(CHANGELOG_URL)
    fg.title("Mistral AI API Changelog")
    fg.link(href=CHANGELOG_URL, rel='alternate')
    fg.description("Latest API updates, model releases, and technical changes from Mistral AI")
    fg.author({'name': 'Mistral AI', 'email': 'support@mistral.ai'})
    fg.language('en')
    fg.lastBuildDate(datetime.now(timezone.utc))
    fg.generator('AI-PULSE RSS Generator')
    fg.image(url='https://docs.mistral.ai/favicon.ico', title='Mistral AI Docs', link=CHANGELOG_URL)
    
    # Add entries to feed
    for entry in sorted(entries, key=lambda x: x['date'], reverse=True):
        fe = fg.add_entry()
        fe.id(entry['url'])
        fe.title(entry['title'])
        fe.link(href=entry['url'])
        fe.description(entry['description'])
        fe.pubDate(entry['date'])
        fe.category(term=entry['category'])
    
    # Ensure output directory exists
    output_path = Path(OUTPUT_FILE)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write feed
    rss_str = fg.rss_str(pretty=True)
    with open(output_path, 'wb') as f:
        f.write(rss_str)
    
    logger.info(f"✅ RSS feed created: {output_path} ({len(entries)} entries)")

def main():
    """Main execution function"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        logger.info("🚀 Starting Mistral AI Changelog RSS generation")
        
        # Fetch and parse page
        soup = get_page_content(CHANGELOG_URL)
        
        # Extract changelog entries
        entries = extract_changelog_entries(soup)
        
        # Create RSS feed
        create_rss_feed(entries)
        
        logger.info(f"✅ Successfully generated RSS feed with {len(entries)} entries")
        
        # Print summary
        if entries:
            logger.info("📋 Latest updates:")
            for entry in entries[:5]:
                logger.info(f"  - {entry['title']}")
        
    except Exception as e:
        logger.error(f"❌ Error generating RSS feed: {e}")
        raise

if __name__ == "__main__":
    main()
