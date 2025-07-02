#!/usr/bin/env python3
"""
AI-PULSE Ukrainian Engineering RSS Generator
Reads English engineering feed and generates Ukrainian translation
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
logger = logging.getLogger('anthropic-engineering-ua')

# Configuration
ENGLISH_FEED_FILE = "feeds/feed_anthropic_engineering.xml"
OUTPUT_FILE = "feeds/feed_anthropic_engineering_ua.xml"
UKRAINIAN_FEED_TITLE = "Anthropic Інженерія - AI-PULSE"
UKRAINIAN_FEED_DESCRIPTION = "Технічні статті та інженерні рішення від Anthropic (українською мовою)"
UKRAINIAN_FEED_LINK = "https://www.anthropic.com/engineering"

async def read_english_feed() -> list:
    """Read and parse English Engineering RSS feed
    
    Returns:
        List of articles from English feed
    """
    feed_path = Path(ENGLISH_FEED_FILE)
    
    if not feed_path.exists():
        logger.error(f"❌ English engineering feed not found: {feed_path}")
        return []
    
    try:
        tree = ET.parse(feed_path)
        root = tree.getroot()
        
        articles = []
        
        # Parse RSS items
        for item in root.findall(".//item"):
            try:
                title_elem = item.find("title")
                link_elem = item.find("link") 
                description_elem = item.find("description")
                category_elem = item.find("category")
                pub_date_elem = item.find("pubDate")
                guid_elem = item.find("guid")
                
                if title_elem is not None and link_elem is not None:
                    article = {
                        'title': title_elem.text or '',
                        'url': link_elem.text or '',
                        'description': description_elem.text or '' if description_elem is not None else '',
                        'category': category_elem.text or 'Engineering' if category_elem is not None else 'Engineering',
                        'pub_date': pub_date_elem.text or '' if pub_date_elem is not None else '',
                        'guid': guid_elem.text or '' if guid_elem is not None else ''
                    }
                    articles.append(article)
                    logger.debug(f"🔧 Parsed: {article['title'][:50]}...")
                    
            except Exception as e:
                logger.warning(f"⚠️ Failed to parse RSS item: {e}")
                continue
        
        logger.info(f"📖 Read {len(articles)} engineering articles from English feed")
        return articles
        
    except Exception as e:
        logger.error(f"❌ Failed to parse English engineering feed: {e}")
        return []

async def generate_ukrainian_rss(articles: list) -> None:
    """Generate Ukrainian Engineering RSS feed from translated articles
    
    Args:
        articles: List of translated articles
    """
    if not articles:
        logger.warning("⚠️ No engineering articles to generate RSS feed")
        return
    
    try:
        # Create RSS feed generator
        fg = FeedGenerator()
        fg.title(UKRAINIAN_FEED_TITLE)
        fg.link(href=UKRAINIAN_FEED_LINK, rel='alternate')
        fg.description(UKRAINIAN_FEED_DESCRIPTION)
        fg.language('uk')  # Ukrainian language code
        fg.generator('AI-PULSE RSS Generator - Ukrainian Engineering Translation')
        fg.docs('http://www.rssboard.org/rss-specification')
        fg.lastBuildDate(datetime.now(timezone.utc))
        
        # Add articles to feed
        for article in articles:
            try:
                fe = fg.add_entry()
                fe.title(article['title'])
                fe.link(href=article['url'])
                fe.description(article['description'])
                fe.guid(article['guid'], permalink=False)
                
                # Add category properly (feedgen expects dict or string)
                if 'category' in article and article['category']:
                    fe.category(term=article['category'])
                
                # Parse and set publication date
                if article['pub_date']:
                    try:
                        # Try to parse existing date or use current time
                        pub_date = datetime.now(timezone.utc)
                        fe.pubDate(pub_date)
                    except:
                        fe.pubDate(datetime.now(timezone.utc))
                else:
                    fe.pubDate(datetime.now(timezone.utc))
                    
                logger.debug(f"➕ Added to RSS: {article['title'][:50]}...")
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to add article to RSS: {e}")
                continue
        
        # Ensure output directory exists
        output_path = Path(OUTPUT_FILE)
        output_path.parent.mkdir(exist_ok=True)
        
        # Write RSS file
        rss_content = fg.rss_str(pretty=True)
        with open(output_path, 'wb') as f:
            f.write(rss_content)
        
        logger.info(f"✅ Ukrainian Engineering RSS feed saved to: {output_path}")
        logger.info(f"📊 Feed contains {len(articles)} articles")
        
    except Exception as e:
        logger.error(f"❌ Failed to generate Ukrainian Engineering RSS feed: {e}")
        raise

async def main():
    """Main function to generate Ukrainian engineering RSS feed"""
    try:
        logger.info("🇺🇦 Starting Ukrainian Anthropic Engineering RSS generation")
        
        # Step 1: Read English feed
        logger.info("📖 Reading English Engineering RSS feed...")
        english_articles = await read_english_feed()
        
        if not english_articles:
            logger.warning("⚠️ No English engineering articles found!")
            return
        
        # Step 2: Translate to Ukrainian
        logger.info("🔄 Translating engineering articles to Ukrainian...")
        translation_engine = TranslationEngine()
        
        translated_articles = await translation_engine.translate_articles_batch(
            english_articles, 
            category="Engineering"
        )
        
        if not translated_articles:
            logger.error("❌ Engineering translation failed!")
            return
        
        # Step 3: Generate Ukrainian RSS
        logger.info("📡 Generating Ukrainian Engineering RSS feed...")
        await generate_ukrainian_rss(translated_articles)
        
        # Step 4: Display cache stats
        cache_stats = translation_engine.get_cache_stats()
        logger.info(f"📚 Translation cache: {cache_stats['total_translations']} entries")
        
        logger.info("🎉 Ukrainian Anthropic Engineering RSS generation completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Engineering generation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
