#!/usr/bin/env python3
"""
Anthropic Alignment Science RSS Feed Generator
Parses alignment.anthropic.com and generates RSS feed

This module scrapes the Anthropic Alignment Science blog and extracts:
- AI safety research posts
- Alignment science findings
- Safety evaluation studies
- Research notes and early findings

Author: AI-PULSE Project
"""

import requests
import logging
from datetime import datetime, timezone
from pathlib import Path
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from urllib.parse import urljoin
import re

# Setup logging
logger = logging.getLogger('anthropic-alignment')

# Configuration
BASE_URL = "https://alignment.anthropic.com"
ALIGNMENT_URL = BASE_URL
OUTPUT_FILE = "feeds/feed_anthropic_alignment.xml"
USER_AGENT = "AI-PULSE RSS Generator 1.0 (github.com/your-username/ai-pulse)"

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

def extract_articles(soup: BeautifulSoup) -> list:
    """Extract alignment research articles with deduplication and better targeting"""
    articles = []
    seen_urls = set()  # For deduplication
    seen_titles = set()  # Additional title-based deduplication
    
    # Find alignment-specific elements with multiple strategies
    
    # Strategy 1: Look for article/post containers
    article_elements = soup.find_all(['article', 'div', 'section'], 
                                   class_=re.compile(r'.*post.*|.*article.*|.*card.*|.*item.*', re.I))
    
    # Strategy 2: Look for links to research papers
    research_links = soup.find_all('a', href=re.compile(r'.*/20\d\d/.*|.*research.*|.*alignment.*'))
    article_elements.extend(research_links)
    
    # Strategy 3: Look for headings that might be article titles
    headings = soup.find_all(['h1', 'h2', 'h3'], string=re.compile(r'.{15,}'))  # Longer headings
    for heading in headings:
        parent = heading.find_parent(['article', 'div', 'section'])
        if parent:
            article_elements.append(parent)
    
    logger.info(f"🔍 Found {len(article_elements)} potential alignment elements")
    
    processed_count = 0
    for element in article_elements[:150]:  # Higher limit for alignment content
        try:
            article = extract_single_article(element)
            if article:
                # Deduplication by URL and title
                url = article['url']
                title = article['title'].lower().strip()
                
                if url not in seen_urls and title not in seen_titles:
                    articles.append(article)
                    seen_urls.add(url)
                    seen_titles.add(title)
                    logger.debug(f"✅ Added: {article['title'][:50]}...")
                else:
                    logger.debug(f"🔄 Skipped duplicate: {article['title'][:50]}...")
            
            processed_count += 1
                    
        except Exception as e:
            logger.debug(f"Error processing alignment element: {e}")
            continue
    
    logger.info(f"🧠 Extracted {len(articles)} unique alignment articles from {processed_count} elements")
    return articles

def extract_single_article(element) -> dict:
    """Extract information from a single alignment research element with improved filtering"""
    article = {}
    
    # Try to find title - be more selective
    title_elem = element.find(['h1', 'h2', 'h3', 'h4'])
    if not title_elem:
        title_elem = element.find('strong') or element
    
    if title_elem:
        title_text = title_elem.get_text(strip=True)
        
        # Filter out junk titles
        junk_patterns = [
            'alignment science team', 'we are anthropic', 'this blog is inspired',
            'welcome to our blog', 'machine learning research', 'contact', 'more'
        ]
        
        # Clean up the title
        clean_title = title_text
        
        # Skip if junk or too short/long
        if (len(clean_title) > 10 and len(clean_title) < 300 and 
            not any(junk in clean_title.lower() for junk in junk_patterns)):
            article['title'] = clean_title
    
    # Try to find URL with better validation
    href = None
    if element.name == 'a':
        href = element.get('href')
    else:
        link_elem = element.find('a')
        href = link_elem.get('href') if link_elem else None
    
    if href:
        # Filter out bad links
        bad_patterns = ['mailto:', 'javascript:', '#research', '#alignment', 'tel:']
        if not any(pattern in href.lower() for pattern in bad_patterns):
            # Handle different domains properly
            if href.startswith('http'):
                article['url'] = href
            elif href.startswith('/'):
                # Determine base URL based on content
                if 'alignment.anthropic.com' in str(element) or '/20' in href:
                    article['url'] = 'https://alignment.anthropic.com' + href
                else:
                    article['url'] = BASE_URL + href
            else:
                article['url'] = urljoin(ALIGNMENT_URL, href)
    
    # Try to extract better description
    description = ""
    desc_elem = element.find(['p', 'div'], class_=re.compile(r'.*desc.*|.*summary.*|.*excerpt.*', re.I))
    if desc_elem:
        description = desc_elem.get_text(strip=True)[:200]
    
    # Look for alignment/safety-related content
    element_text = element.get_text().lower()
    alignment_keywords = ['alignment', 'safety', 'research', 'ai safety', 'faking',
                         'interpretability', 'steering', 'control', 'evaluation', 
                         'risk', 'monitoring', 'deception', 'honesty', 'sleeper',
                         'sabotage', 'sandbagging', 'forecasting']
    
    has_alignment_content = any(keyword in element_text for keyword in alignment_keywords)
    
    # Only return if we have title, URL, and alignment-related content
    if 'title' in article and 'url' in article and has_alignment_content:
        article['category'] = 'Alignment Science'
        article['pub_date'] = datetime.now(timezone.utc)
        
        # Better description
        if description:
            article['description'] = f"AI Safety research: {description[:120]}..."
        else:
            article['description'] = f"AI Safety research from Anthropic: {article['title']}"
        
        return article
    
    return None

def generate_rss_feed(articles: list) -> None:
    """Generate RSS feed from alignment research articles"""
    logger.info("📡 Generating Alignment Science RSS feed...")
    
    # Create feed generator
    fg = FeedGenerator()
    fg.title('Anthropic Alignment Science - AI-PULSE')
    fg.link(href=ALIGNMENT_URL, rel='alternate')
    fg.description('AI safety research and alignment science from Anthropic')
    fg.language('en')
    fg.lastBuildDate(datetime.now(timezone.utc))
    fg.generator('AI-PULSE RSS Generator')
    
    # Add articles to feed
    for article in articles[:40]:  # Research posts can be substantial
        fe = fg.add_entry()
        fe.title(article['title'])
        fe.link(href=article['url'])
        fe.description(article['description'])
        fe.category(term=article['category'])
        fe.pubDate(article['pub_date'])
        fe.guid(article['url'], False)
    
    # Ensure output directory exists
    output_path = Path(OUTPUT_FILE)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write RSS feed
    fg.rss_file(OUTPUT_FILE)
    logger.info(f"✅ Alignment Science RSS feed saved to: {OUTPUT_FILE}")
    logger.info(f"📊 Feed contains {len(articles)} articles")

def main():
    """Main execution function"""
    try:
        logger.info("🚀 Starting Anthropic Alignment Science RSS generation")
        
        # Fetch and parse the alignment blog
        soup = get_page_content(ALIGNMENT_URL)
        
        # Extract articles
        articles = extract_articles(soup)
        
        # Generate RSS feed
        generate_rss_feed(articles)
        
        logger.info("🎉 Anthropic Alignment Science RSS generation completed!")
        
    except Exception as e:
        logger.error(f"💥 Fatal error in alignment feed: {e}")
        raise

if __name__ == "__main__":
    main()
