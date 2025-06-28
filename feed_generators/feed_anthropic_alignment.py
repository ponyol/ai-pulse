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
    """Extract alignment research articles from the page"""
    articles = []
    
    # Look for research posts and blog entries
    post_elements = soup.find_all(['article', 'div', 'section', 'li'], 
                                 class_=re.compile(r'.*post.*|.*article.*|.*entry.*', re.I))
    
    # Also look for simple text content and headers
    if not post_elements:
        post_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'a'])
    
    logger.info(f"🔍 Found {len(post_elements)} potential alignment elements")
    
    for element in post_elements:
        try:
            article = extract_single_article(element)
            if article:
                articles.append(article)
        except Exception as e:
            logger.debug(f"Error processing alignment article: {e}")
            continue
    
    # Add some default/known alignment research topics if no articles found
    if not articles:
        default_articles = [
            {
                'title': 'Alignment faking in large language models',
                'url': f'{BASE_URL}/2024/alignment-faking/',
                'category': 'Alignment Research',
                'description': 'Research on how AI models might fake alignment during training',
                'pub_date': datetime.now(timezone.utc)
            },
            {
                'title': 'Anthropic Alignment Science Blog',
                'url': ALIGNMENT_URL,
                'category': 'Alignment Science',
                'description': 'Research on steering and controlling future powerful AI systems',
                'pub_date': datetime.now(timezone.utc)
            }
        ]
        articles.extend(default_articles)
    
    logger.info(f"🧠 Extracted {len(articles)} alignment articles")
    return articles

def extract_single_article(element) -> dict:
    """Extract information from a single alignment research element"""
    article = {}
    
    # Try to find title
    title_elem = element.find(['h1', 'h2', 'h3', 'h4']) or element
    if title_elem:
        title_text = title_elem.get_text(strip=True)
        # Look for research-related titles
        if len(title_text) > 10:
            article['title'] = title_text
    
    # Try to find URL
    if element.name == 'a':
        href = element.get('href')
    else:
        link_elem = element.find('a')
        href = link_elem.get('href') if link_elem else None
    
    if href:
        article['url'] = urljoin(BASE_URL, href)
    
    # Look for alignment/safety-related content
    element_text = element.get_text().lower()
    alignment_keywords = ['alignment', 'safety', 'research', 'ai safety', 'faking',
                         'interpretability', 'steering', 'control', 'evaluation', 
                         'risk', 'monitoring', 'deception', 'honesty']
    
    has_alignment_content = any(keyword in element_text for keyword in alignment_keywords)
    
    # Only return if we have title, URL, and alignment-related content
    if 'title' in article and 'url' in article and has_alignment_content:
        article['category'] = 'Alignment Science'
        article['pub_date'] = datetime.now(timezone.utc)
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
