#!/usr/bin/env python3
"""
AI-PULSE Ukrainian Alignment Science RSS Generator
Reads English alignment feed and generates Ukrainian translation
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
logger = logging.getLogger('anthropic-alignment-ua')

# Configuration
ENGLISH_FEED_FILE = "feeds/feed_anthropic_alignment.xml"
OUTPUT_FILE = "feeds/feed_anthropic_alignment_ua.xml"
UKRAINIAN_FEED_TITLE = "Anthropic Безпека ШІ - AI-PULSE"
UKRAINIAN_FEED_DESCRIPTION = "Дослідження безпеки ШІ та alignment від Anthropic (українською мовою)"
UKRAINIAN_FEED_LINK = "https://alignment.anthropic.com"

async def read_english_feed() -> list:
    """Read and parse English Alignment Science RSS feed
    
    Returns:
        List of articles from English feed
    """
    feed_path = Path(ENGLISH_FEED_FILE)
    
    if not feed_path.exists():
        logger.error(f"❌ English alignment feed not found: {feed_path}")
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
                        'category': category_elem.text or 'Alignment Science' if category_elem is not None else 'Alignment Science',
                        'pub_date': pub_date_elem.text or '' if pub_date_elem is not None else '',
                        'guid': guid_elem.text or '' if guid_elem is not None else ''
                    }
                    articles.append(article)
                    logger.debug(f"🧠 Parsed: {article['title'][:50]}...")
                    
            except Exception as e:
                logger.warning(f"⚠️ Failed to parse RSS item: {e}")
                continue
        
        logger.info(f"📖 Read {len(articles)} alignment science articles from English feed")
        return articles
        
    except Exception as e:
        logger.error(f"❌ Failed to parse English alignment feed: {e}")
        return []

async def generate_ukrainian_rss(articles: list) -> None:
    """Generate Ukrainian Alignment Science RSS feed from translated articles
    
    Args:
        articles: List of translated articles
    """
    if not articles:
        logger.warning("⚠️ No alignment science articles to generate RSS feed")
        return
    
    try:
        # Create RSS feed generator
        fg = FeedGenerator()
        fg.title(UKRAINIAN_FEED_TITLE)
        fg.link(href=UKRAINIAN_FEED_LINK, rel='alternate')
        fg.description(UKRAINIAN_FEED_DESCRIPTION)
        fg.language('uk')  # Ukrainian language code
        fg.generator('AI-PULSE RSS Generator - Ukrainian Alignment Science Translation')
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
        
        logger.info(f"✅ Ukrainian Alignment Science RSS feed saved to: {output_path}")
        logger.info(f"📊 Feed contains {len(articles)} articles")
        
    except Exception as e:
        logger.error(f"❌ Failed to generate Ukrainian Alignment Science RSS feed: {e}")
        raise

async def main():
    """Main function to generate Ukrainian alignment science RSS feed"""
    try:
        logger.info("🇺🇦 Starting Ukrainian Anthropic Alignment Science RSS generation")
        
        # Step 1: Read English feed
        logger.info("📖 Reading English Alignment Science RSS feed...")
        english_articles = await read_english_feed()
        
        if not english_articles:
            logger.warning("⚠️ No English alignment science articles found!")
            return
        
        # Step 2: Translate to Ukrainian
        logger.info("🔄 Translating alignment science articles to Ukrainian...")
        translation_engine = TranslationEngine()
        
        translated_articles = await translation_engine.translate_articles_batch(
            english_articles, 
            category="Alignment Science"
        )
        
        if not translated_articles:
            logger.error("❌ Alignment Science translation failed!")
            return
        
        # Step 3: Generate Ukrainian RSS
        logger.info("📡 Generating Ukrainian Alignment Science RSS feed...")
        await generate_ukrainian_rss(translated_articles)
        
        # Step 4: Display cache stats
        cache_stats = translation_engine.get_cache_stats()
        logger.info(f"📚 Translation cache: {cache_stats['total_translations']} entries")
        
        logger.info("🎉 Ukrainian Anthropic Alignment Science RSS generation completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Alignment Science generation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
