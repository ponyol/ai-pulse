#!/usr/bin/env python3
"""
Anthropic Engineering RSS Feed Generator
Parses anthropic.com/engineering and generates RSS feed

This module scrapes the Anthropic engineering blog and extracts:
- Technical blog posts
- Engineering insights
- Development updates
- Technical documentation

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
logger = logging.getLogger('anthropic-engineering')

# Configuration
BASE_URL = "https://www.anthropic.com"
ENGINEERING_URL = f"{BASE_URL}/engineering"
OUTPUT_FILE = "feeds/feed_anthropic_engineering.xml"
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
    """Extract engineering articles from the page"""
    articles = []
    
    # Look for engineering posts - may have different structure than news
    post_elements = soup.find_all(['article', 'div', 'section'], 
                                 class_=re.compile(r'.*post.*|.*article.*|.*featured.*', re.I))
    
    # Also check for simple links and headers
    if not post_elements:
        post_elements = soup.find_all(['a', 'h1', 'h2', 'h3'])
    
    logger.info(f"🔍 Found {len(post_elements)} potential engineering post elements")
    
    for element in post_elements:
        try:
            article = extract_single_article(element)
            if article:
                articles.append(article)
        except Exception as e:
            logger.debug(f"Error processing engineering post: {e}")
            continue
    
    # If no articles found, create a default entry about the engineering team
    if not articles:
        articles.append({
            'title': 'Anthropic Engineering Team',
            'url': ENGINEERING_URL,
            'category': 'Engineering',
            'description': 'Inside the team building reliable AI systems at Anthropic',
            'pub_date': datetime.now(timezone.utc)
        })
    
    logger.info(f"🔧 Extracted {len(articles)} engineering articles")
    return articles

def extract_single_article(element) -> dict:
    """Extract information from a single engineering post element"""
    article = {}
    
    # Try to find title
    title_elem = element.find(['h1', 'h2', 'h3', 'h4']) or element
    if title_elem:
        title_text = title_elem.get_text(strip=True)
        # Engineering posts typically have meaningful titles
        if len(title_text) > 5 and 'engineering' not in title_text.lower():
            article['title'] = title_text
    
    # Try to find URL
    if element.name == 'a':
        href = element.get('href')
    else:
        link_elem = element.find('a')
        href = link_elem.get('href') if link_elem else None
    
    if href:
        article['url'] = urljoin(BASE_URL, href)
    
    # Look for engineering-related content
    element_text = element.get_text().lower()
    engineering_keywords = ['coding', 'development', 'technical', 'engineering', 
                           'architecture', 'system', 'api', 'infrastructure']
    
    has_engineering_content = any(keyword in element_text for keyword in engineering_keywords)
    
    # Only return if we have title and URL, and it seems engineering-related
    if 'title' in article and 'url' in article and has_engineering_content:
        article['category'] = 'Engineering'
        article['pub_date'] = datetime.now(timezone.utc)
        article['description'] = f"Engineering insights from Anthropic: {article['title']}"
        return article
    
    return None

def generate_rss_feed(articles: list) -> None:
    """Generate RSS feed from engineering articles"""
    logger.info("📡 Generating Engineering RSS feed...")
    
    # Create feed generator
    fg = FeedGenerator()
    fg.title('Anthropic Engineering - AI-PULSE')
    fg.link(href=ENGINEERING_URL, rel='alternate')
    fg.description('Technical insights and engineering updates from Anthropic')
    fg.language('en')
    fg.lastBuildDate(datetime.now(timezone.utc))
    fg.generator('AI-PULSE RSS Generator')
    
    # Add articles to feed
    for article in articles[:30]:  # Engineering posts are typically fewer
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
    logger.info(f"✅ Engineering RSS feed saved to: {OUTPUT_FILE}")
    logger.info(f"📊 Feed contains {len(articles)} articles")

def main():
    """Main execution function"""
    try:
        logger.info("🚀 Starting Anthropic Engineering RSS generation")
        
        # Fetch and parse the engineering page
        soup = get_page_content(ENGINEERING_URL)
        
        # Extract articles
        articles = extract_articles(soup)
        
        # Generate RSS feed
        generate_rss_feed(articles)
        
        logger.info("🎉 Anthropic Engineering RSS generation completed!")
        
    except Exception as e:
        logger.error(f"💥 Fatal error in engineering feed: {e}")
        raise

if __name__ == "__main__":
    main()
