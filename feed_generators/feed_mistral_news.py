#!/usr/bin/env python3
"""
Mistral AI News RSS Feed Generator
Parses mistral.ai/news and generates RSS feed

This module scrapes the main Mistral AI news page and extracts:
- Article titles
- Publication dates  
- Article URLs
- Categories/tags
- Images (if available)

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
import json

# Setup logging
logger = logging.getLogger('mistral-news')

# Configuration
BASE_URL = "https://mistral.ai"
NEWS_URL = f"{BASE_URL}/news"
OUTPUT_FILE = "feeds/feed_mistral_news.xml"
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

def extract_articles(soup: BeautifulSoup) -> list:
    """Extract article information from the Mistral news page"""
    articles = []
    seen_urls = set()
    seen_titles = set()
    
    # Look for various patterns that might contain news articles
    # Mistral likely uses modern React/Next.js so look for common patterns
    article_elements = []
    
    # Pattern 1: Look for links to /news/ articles
    news_links = soup.find_all('a', href=re.compile(r'.*/news/.*'))
    article_elements.extend(news_links)
    
    # Pattern 2: Look for common article containers
    containers = soup.find_all(['div', 'article', 'section'], 
                              class_=re.compile(r'.*(card|item|post|article|news).*', re.I))
    article_elements.extend(containers)
    
    # Pattern 3: Look for structured data or JSON-LD
    scripts = soup.find_all('script', type='application/ld+json')
    for script in scripts:
        try:
            data = json.loads(script.string)
            if isinstance(data, dict) and 'headline' in data:
                # This might be a news article in JSON-LD format
                article = extract_from_json_ld(data)
                if article:
                    articles.append(article)
        except:
            continue
    
    logger.info(f"🔍 Found {len(article_elements)} potential article elements")
    
    for element in article_elements[:50]:
        try:
            article = extract_single_article(element)
            if article:
                url = article['url']
                title = article['title'].lower().strip()
                
                if url not in seen_urls and title not in seen_titles:
                    articles.append(article)
                    seen_urls.add(url)
                    seen_titles.add(title)
                    logger.debug(f"✅ Added: {article['title'][:50]}...")
                    
        except Exception as e:
            logger.debug(f"Error processing article element: {e}")
            continue
    
    logger.info(f"📰 Extracted {len(articles)} unique articles")
    return articles

def extract_from_json_ld(data: dict) -> dict:
    """Extract article from JSON-LD structured data"""
    try:
        article = {
            'title': data.get('headline', ''),
            'url': data.get('url', ''),
            'date': parse_date(data.get('datePublished', '')),
            'description': data.get('description', ''),
            'category': 'News',
            'image': data.get('image', {}).get('url', '') if isinstance(data.get('image'), dict) else str(data.get('image', ''))
        }
        
        if article['title'] and article['url']:
            return article
    except:
        pass
    return None

def extract_single_article(element) -> dict:
    """Extract information from a single article element"""
    article = {}
    
    # Find URL
    url = None
    if element.name == 'a' and element.get('href'):
        url = element.get('href')
    else:
        link = element.find('a', href=True)
        if link:
            url = link.get('href')
    
    if not url:
        return None
    
    # Make URL absolute
    if url.startswith('/'):
        url = urljoin(BASE_URL, url)
    elif not url.startswith('http'):
        return None
    
    # Filter for Mistral news articles
    if '/news/' not in url:
        return None
    
    # Find title
    title = None
    title_elem = element.find(['h1', 'h2', 'h3', 'h4', 'h5'])
    if title_elem:
        title = title_elem.get_text(strip=True)
    else:
        # Fallback to link text or element text
        if element.name == 'a':
            title = element.get_text(strip=True)
        else:
            # Look for any strong text
            strong = element.find('strong')
            if strong:
                title = strong.get_text(strip=True)
            else:
                title = element.get_text(strip=True)[:100]  # Limit fallback text
    
    if not title or len(title) < 10:
        return None
    
    # Find date
    date = None
    date_elem = element.find(['time', 'span'], class_=re.compile(r'.*(date|time).*', re.I))
    if date_elem:
        date_text = date_elem.get_text(strip=True) or date_elem.get('datetime', '')
        date = parse_date(date_text)
    
    # Find description
    description = ''
    desc_elem = element.find(['p', 'div'], class_=re.compile(r'.*(desc|summary|excerpt).*', re.I))
    if desc_elem:
        description = desc_elem.get_text(strip=True)
    
    # Find image
    image = ''
    img_elem = element.find('img')
    if img_elem:
        image = img_elem.get('src', '') or img_elem.get('data-src', '')
        if image and image.startswith('/'):
            image = urljoin(BASE_URL, image)
    
    # Determine category (basic heuristic)
    category = 'News'
    if any(word in title.lower() for word in ['api', 'model', 'release']):
        category = 'Product'
    elif any(word in title.lower() for word in ['research', 'paper']):
        category = 'Research'
    
    return {
        'title': title,
        'url': url,
        'date': date or datetime.now(timezone.utc),
        'description': description,
        'category': category,
        'image': image
    }

def parse_date(date_str: str) -> datetime:
    """Parse various date formats"""
    if not date_str:
        return datetime.now(timezone.utc)
    
    # Common date formats
    formats = [
        '%Y-%m-%d',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%dT%H:%M:%S.%fZ',
        '%B %d, %Y',
        '%b %d, %Y',
        '%d %B %Y',
        '%d %b %Y'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    
    # Fallback: extract year if possible
    year_match = re.search(r'\b(20\d{2})\b', date_str)
    if year_match:
        try:
            year = int(year_match.group(1))
            return datetime(year, 1, 1, tzinfo=timezone.utc)
        except:
            pass
    
    return datetime.now(timezone.utc)

def create_rss_feed(articles: list) -> None:
    """Create RSS feed from articles"""
    if not articles:
        logger.warning("No articles found, creating empty feed")
    
    # Create feed
    fg = FeedGenerator()
    fg.id(NEWS_URL)
    fg.title("Mistral AI News")
    fg.link(href=NEWS_URL, rel='alternate')
    fg.description("Latest news and updates from Mistral AI - AI research lab building the best open source models in the world")
    fg.author({'name': 'Mistral AI', 'email': 'contact@mistral.ai'})
    fg.language('en')
    fg.lastBuildDate(datetime.now(timezone.utc))
    fg.generator('AI-PULSE RSS Generator')
    fg.image(url='https://mistral.ai/favicon.ico', title='Mistral AI', link=NEWS_URL)
    
    # Add articles to feed
    for article in sorted(articles, key=lambda x: x['date'], reverse=True):
        fe = fg.add_entry()
        fe.id(article['url'])
        fe.title(article['title'])
        fe.link(href=article['url'])
        fe.description(article['description'] or article['title'])
        fe.pubDate(article['date'])
        fe.category(term=article['category'])
        
        if article['image']:
            fe.enclosure(article['image'], '0', 'image/jpeg')
    
    # Ensure output directory exists
    output_path = Path(OUTPUT_FILE)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write feed
    rss_str = fg.rss_str(pretty=True)
    with open(output_path, 'wb') as f:
        f.write(rss_str)
    
    logger.info(f"✅ RSS feed created: {output_path} ({len(articles)} articles)")

def main():
    """Main execution function"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        logger.info("🚀 Starting Mistral AI News RSS generation")
        
        # Fetch and parse page
        soup = get_page_content(NEWS_URL)
        
        # Extract articles
        articles = extract_articles(soup)
        
        # Create RSS feed
        create_rss_feed(articles)
        
        logger.info(f"✅ Successfully generated RSS feed with {len(articles)} articles")
        
        # Print summary
        if articles:
            logger.info("📋 Latest articles:")
            for article in articles[:5]:
                logger.info(f"  - {article['title']}")
                logger.info(f"    {article['url']}")
        
    except Exception as e:
        logger.error(f"❌ Error generating RSS feed: {e}")
        raise

if __name__ == "__main__":
    main()
