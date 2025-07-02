#!/usr/bin/env python3
"""
AI-PULSE Ukrainian Mistral Complete RSS Generator
Combines all Mistral AI Ukrainian feeds into one comprehensive feed

This module aggregates Ukrainian translations from:
- Mistral AI News (Ukrainian)
- Mistral AI API Changelog (Ukrainian)

Author: AI-PULSE Project
"""

import sys
import json
import logging
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from feedgen.feed import FeedGenerator
import xml.etree.ElementTree as ET

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('mistral-complete-ua')

# Configuration
FEED_FILES = {
    'News': 'feeds/feed_mistral_news_ua.xml',
    'Changelog': 'feeds/feed_mistral_changelog_ua.xml'
}
OUTPUT_FILE = "feeds/feed_mistral_complete_ua.xml"
UKRAINIAN_FEED_TITLE = "Mistral AI Повний Огляд - AI-PULSE"
UKRAINIAN_FEED_DESCRIPTION = "Повне покриття Mistral AI: новини, оголошення продуктів, оновлення API та технічні зміни (українською мовою)"
UKRAINIAN_FEED_LINK = "https://mistral.ai/"

async def read_ukrainian_feeds() -> list:
    """Read and combine all Ukrainian RSS feeds
    
    Returns:
        Combined list of articles from all Ukrainian feeds
    """
    all_articles = []
    
    for source_name, feed_file in FEED_FILES.items():
        feed_path = Path(feed_file)
        
        if not feed_path.exists():
            logger.warning(f"⚠️ Ukrainian feed not found: {feed_path}")
            continue
        
        try:
            tree = ET.parse(feed_path)
            root = tree.getroot()
            
            source_articles = []
            
            # Parse RSS items
            for item in root.findall('.//item'):
                try:
                    title_elem = item.find('title')
                    description_elem = item.find('description')
                    link_elem = item.find('link')
                    pubdate_elem = item.find('pubDate')
                    category_elem = item.find('category')
                    
                    if title_elem is not None and link_elem is not None:
                        article = {
                            'title': title_elem.text or '',
                            'description': description_elem.text or '' if description_elem is not None else '',
                            'link': link_elem.text or '',
                            'pubdate': pubdate_elem.text or '' if pubdate_elem is not None else '',
                            'category': category_elem.text or source_name if category_elem is not None else source_name,
                            'source': source_name
                        }
                        source_articles.append(article)
                        
                except Exception as e:
                    logger.warning(f"⚠️ Error parsing RSS item from {source_name}: {e}")
                    continue
            
            all_articles.extend(source_articles)
            logger.info(f"📖 Read {len(source_articles)} articles from {source_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to parse {source_name} feed: {e}")
            continue
    
    logger.info(f"📚 Total articles from all Ukrainian feeds: {len(all_articles)}")
    return all_articles

async def sort_articles_by_date(articles: list) -> list:
    """Sort articles by publication date (newest first)
    
    Args:
        articles: List of articles to sort
        
    Returns:
        Sorted list of articles
    """
    def parse_rfc_date(date_str: str) -> datetime:
        """Parse RFC 2822 date format"""
        if not date_str:
            return datetime.now(timezone.utc)
        
        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except:
            return datetime.now(timezone.utc)
    
    # Sort by parsed date
    sorted_articles = sorted(
        articles, 
        key=lambda x: parse_rfc_date(x.get('pubdate', '')), 
        reverse=True
    )
    
    logger.info(f"📅 Sorted {len(sorted_articles)} articles by date")
    return sorted_articles

async def create_complete_ukrainian_feed(articles: list) -> None:
    """Create comprehensive Ukrainian RSS feed from all articles
    
    Args:
        articles: List of Ukrainian articles
    """
    if not articles:
        logger.warning("⚠️ No articles to include in complete feed")
    
    # Create feed generator
    fg = FeedGenerator()
    fg.id(UKRAINIAN_FEED_LINK)
    fg.title(UKRAINIAN_FEED_TITLE)
    fg.link(href=UKRAINIAN_FEED_LINK, rel='alternate')
    fg.description(UKRAINIAN_FEED_DESCRIPTION)
    fg.author({'name': 'Mistral AI (Повний український переклад)', 'email': 'contact@mistral.ai'})
    fg.language('uk')  # Ukrainian language code
    fg.lastBuildDate(datetime.now(timezone.utc))
    fg.generator('AI-PULSE RSS Generator - Complete Ukrainian Translation')
    fg.image(url='https://mistral.ai/favicon.ico', title='Mistral AI Повний Огляд', link=UKRAINIAN_FEED_LINK)
    
    # Add articles to feed
    for article in articles:
        try:
            fe = fg.add_entry()
            fe.id(article['link'])
            
            # Add source prefix to title for clarity
            source_mapping = {
                'News': 'Новини',
                'Changelog': 'Changelog'
            }
            source_ua = source_mapping.get(article.get('source', ''), article.get('source', ''))
            title = f"[{source_ua}] {article['title']}"
            
            fe.title(title)
            fe.link(href=article['link'])
            
            # Enhanced description with source info
            description = article.get('description', article['title'])
            if article.get('source'):
                source_desc = f"Джерело: {source_ua}\n\n{description}"
                fe.description(source_desc)
            else:
                fe.description(description)
            
            fe.category(term=article['category'])
            
            # Parse publication date
            if article['pubdate']:
                try:
                    from email.utils import parsedate_to_datetime
                    pubdate = parsedate_to_datetime(article['pubdate'])
                    fe.pubDate(pubdate)
                except:
                    fe.pubDate(datetime.now(timezone.utc))
            else:
                fe.pubDate(datetime.now(timezone.utc))
                
        except Exception as e:
            logger.warning(f"⚠️ Error adding article to complete feed: {e}")
            continue
    
    # Ensure output directory exists
    output_path = Path(OUTPUT_FILE)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write feed
    try:
        rss_str = fg.rss_str(pretty=True)
        with open(output_path, 'wb') as f:
            f.write(rss_str)
        
        logger.info(f"✅ Complete Ukrainian RSS feed created: {output_path} ({len(articles)} articles)")
        
    except Exception as e:
        logger.error(f"❌ Failed to write complete Ukrainian feed: {e}")
        raise

async def main():
    """Main execution function"""
    try:
        logger.info("🚀 Starting Complete Ukrainian Mistral RSS generation")
        
        # Step 1: Read all Ukrainian feeds
        logger.info("📖 Reading all Ukrainian feeds...")
        articles = await read_ukrainian_feeds()
        
        if not articles:
            logger.error("❌ No articles found in Ukrainian feeds")
            return
        
        # Step 2: Sort articles by date
        logger.info("📅 Sorting articles by date...")
        sorted_articles = await sort_articles_by_date(articles)
        
        # Step 3: Create complete Ukrainian feed
        logger.info("📝 Creating complete Ukrainian RSS feed...")
        await create_complete_ukrainian_feed(sorted_articles)
        
        logger.info("✅ Complete Ukrainian Mistral RSS generation completed successfully!")
        
        # Print summary
        logger.info("📋 Generated complete feed summary:")
        logger.info(f"  📰 Total articles: {len(sorted_articles)}")
        
        # Summary by source
        source_counts = {}
        for article in sorted_articles:
            source = article.get('source', 'Unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        logger.info("  📊 By source:")
        for source, count in source_counts.items():
            source_mapping = {'News': 'Новини', 'Changelog': 'Changelog'}
            source_ua = source_mapping.get(source, source)
            logger.info(f"    {source_ua}: {count} статей")
        
        if sorted_articles:
            logger.info("  🔝 Latest articles (Ukrainian):")
            for article in sorted_articles[:3]:
                source = article.get('source', 'Unknown')
                source_mapping = {'News': 'Новини', 'Changelog': 'Changelog'}
                source_ua = source_mapping.get(source, source)
                logger.info(f"    [{source_ua}] {article['title']}")
        
    except Exception as e:
        logger.error(f"❌ Error in complete Ukrainian RSS generation: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
