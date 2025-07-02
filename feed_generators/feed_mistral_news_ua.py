#!/usr/bin/env python3
"""
AI-PULSE Ukrainian Mistral News RSS Generator
Reads English Mistral news feed and generates Ukrainian translation
"""

import sys
import json
import logging
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from feedgen.feed import FeedGenerator
import xml.etree.ElementTree as ET

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent))

from translation_engine import TranslationEngine

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('mistral-news-ua')

# Configuration
ENGLISH_FEED_FILE = "feeds/feed_mistral_news.xml"
OUTPUT_FILE = "feeds/feed_mistral_news_ua.xml"
UKRAINIAN_FEED_TITLE = "Mistral AI Новини - AI-PULSE"
UKRAINIAN_FEED_DESCRIPTION = "Останні новини та оголошення від Mistral AI (українською мовою)"
UKRAINIAN_FEED_LINK = "https://mistral.ai/news"

async def read_english_feed() -> list:
    """Read and parse English RSS feed
    
    Returns:
        List of articles from English feed
    """
    feed_path = Path(ENGLISH_FEED_FILE)
    
    if not feed_path.exists():
        logger.error(f"❌ English feed not found: {feed_path}")
        return []
    
    try:
        tree = ET.parse(feed_path)
        root = tree.getroot()
        
        articles = []
        
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
                        'category': category_elem.text or 'News' if category_elem is not None else 'News'
                    }
                    articles.append(article)
                    logger.debug(f"✅ Parsed article: {article['title'][:50]}...")
                    
            except Exception as e:
                logger.warning(f"⚠️ Error parsing RSS item: {e}")
                continue
        
        logger.info(f"📖 Read {len(articles)} articles from English feed")
        return articles
        
    except Exception as e:
        logger.error(f"❌ Failed to parse English feed: {e}")
        return []

async def translate_articles(articles: list) -> list:
    """Translate articles to Ukrainian
    
    Args:
        articles: List of articles to translate
        
    Returns:
        List of translated articles
    """
    if not articles:
        logger.warning("⚠️ No articles to translate")
        return []
    
    logger.info(f"🌐 Starting translation of {len(articles)} articles")
    
    # Initialize translation engine
    translator = TranslationEngine()
    
    # Translate articles in batches for efficiency
    translated_articles = await translator.translate_articles_batch(articles)
    
    logger.info(f"✅ Translation completed: {len(translated_articles)} articles")
    return translated_articles

async def create_ukrainian_feed(articles: list) -> None:
    """Create Ukrainian RSS feed from translated articles
    
    Args:
        articles: List of translated articles
    """
    if not articles:
        logger.warning("⚠️ No articles to include in feed")
    
    # Create feed generator
    fg = FeedGenerator()
    fg.id(UKRAINIAN_FEED_LINK)
    fg.title(UKRAINIAN_FEED_TITLE)
    fg.link(href=UKRAINIAN_FEED_LINK, rel='alternate')
    fg.description(UKRAINIAN_FEED_DESCRIPTION)
    fg.author({'name': 'Mistral AI (Ukrainian Translation)', 'email': 'contact@mistral.ai'})
    fg.language('uk')  # Ukrainian language code
    fg.lastBuildDate(datetime.now(timezone.utc))
    fg.generator('AI-PULSE RSS Generator - Ukrainian Translation')
    fg.image(url='https://mistral.ai/favicon.ico', title='Mistral AI', link=UKRAINIAN_FEED_LINK)
    
    # Add articles to feed
    for article in articles:
        try:
            fe = fg.add_entry()
            fe.id(article['link'])
            fe.title(article['title_ua'])
            fe.link(href=article['link'])
            fe.description(article['description_ua'])
            fe.category(term=article['category_ua'])
            
            # Parse publication date
            if article['pubdate']:
                try:
                    # Try to parse RFC 2822 format first
                    from email.utils import parsedate_to_datetime
                    pubdate = parsedate_to_datetime(article['pubdate'])
                    fe.pubDate(pubdate)
                except:
                    # Fallback to current time if parsing fails
                    fe.pubDate(datetime.now(timezone.utc))
            else:
                fe.pubDate(datetime.now(timezone.utc))
                
        except Exception as e:
            logger.warning(f"⚠️ Error adding article to feed: {e}")
            continue
    
    # Ensure output directory exists
    output_path = Path(OUTPUT_FILE)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write feed
    try:
        rss_str = fg.rss_str(pretty=True)
        with open(output_path, 'wb') as f:
            f.write(rss_str)
        
        logger.info(f"✅ Ukrainian RSS feed created: {output_path} ({len(articles)} articles)")
        
    except Exception as e:
        logger.error(f"❌ Failed to write Ukrainian feed: {e}")
        raise

async def main():
    """Main execution function"""
    try:
        logger.info("🚀 Starting Ukrainian Mistral News RSS generation")
        
        # Step 1: Read English feed
        logger.info("📖 Reading English feed...")
        articles = await read_english_feed()
        
        if not articles:
            logger.error("❌ No articles found in English feed")
            return
        
        # Step 2: Translate articles
        logger.info("🌐 Translating articles to Ukrainian...")
        translated_articles = await translate_articles(articles)
        
        if not translated_articles:
            logger.error("❌ Translation failed")
            return
        
        # Step 3: Create Ukrainian feed
        logger.info("📝 Creating Ukrainian RSS feed...")
        await create_ukrainian_feed(translated_articles)
        
        logger.info("✅ Ukrainian Mistral News RSS generation completed successfully!")
        
        # Print summary
        logger.info("📋 Generated feed summary:")
        logger.info(f"  📰 Total articles: {len(translated_articles)}")
        if translated_articles:
            logger.info("  🔤 Latest articles (Ukrainian):")
            for article in translated_articles[:3]:
                logger.info(f"    - {article['title_ua']}")
        
    except Exception as e:
        logger.error(f"❌ Error in Ukrainian RSS generation: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
