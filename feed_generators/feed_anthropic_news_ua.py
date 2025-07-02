#!/usr/bin/env python3
"""
AI-PULSE Ukrainian News RSS Generator
Reads English news feed and generates Ukrainian translation
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
logger = logging.getLogger('anthropic-news-ua')

# Configuration
ENGLISH_FEED_FILE = "feeds/feed_anthropic_news.xml"
OUTPUT_FILE = "feeds/feed_anthropic_news_ua.xml"
UKRAINIAN_FEED_TITLE = "Anthropic Новини - AI-PULSE"
UKRAINIAN_FEED_DESCRIPTION = "Останні новини та оголошення від Anthropic (українською мовою)"
UKRAINIAN_FEED_LINK = "https://www.anthropic.com/news"

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
                        'category': category_elem.text or 'News' if category_elem is not None else 'News',
                        'pub_date': pub_date_elem.text or '' if pub_date_elem is not None else '',
                        'guid': guid_elem.text or '' if guid_elem is not None else ''
                    }
                    articles.append(article)
                    logger.debug(f"📰 Parsed: {article['title'][:50]}...")
                    
            except Exception as e:
                logger.warning(f"⚠️ Failed to parse RSS item: {e}")
                continue
        
        logger.info(f"📖 Read {len(articles)} articles from English feed")
        return articles
        
    except Exception as e:
        logger.error(f"❌ Failed to parse English feed: {e}")
        return []

async def generate_ukrainian_rss(articles: list) -> None:
    """Generate Ukrainian RSS feed from translated articles
    
    Args:
        articles: List of translated articles
    """
    if not articles:
        logger.warning("⚠️ No articles to generate RSS feed")
        return
    
    try:
        # Create RSS feed generator
        fg = FeedGenerator()
        fg.title(UKRAINIAN_FEED_TITLE)
        fg.link(href=UKRAINIAN_FEED_LINK, rel='alternate')
        fg.description(UKRAINIAN_FEED_DESCRIPTION)
        fg.language('uk')  # Ukrainian language code
        fg.generator('AI-PULSE RSS Generator - Ukrainian Translation')
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
        
        logger.info(f"✅ Ukrainian RSS feed saved to: {output_path}")
        logger.info(f"📊 Feed contains {len(articles)} articles")
        
    except Exception as e:
        logger.error(f"❌ Failed to generate Ukrainian RSS feed: {e}")
        raise

async def main():
    """Main function to generate Ukrainian news RSS feed"""
    try:
        logger.info("🇺🇦 Starting Ukrainian Anthropic News RSS generation")
        start_time = datetime.now()
        
        # Step 1: Read English feed
        logger.info("📖 Reading English RSS feed...")
        english_articles = await read_english_feed()
        
        if not english_articles:
            logger.error("❌ No English articles found!")
            return
        
        logger.info(f"📰 Found {len(english_articles)} English articles to translate")
        
        # Step 2: Translate to Ukrainian  
        logger.info("🔄 Initializing Ukrainian translation engine...")
        translation_engine = TranslationEngine()
        
        # Show translation engine status
        cache_stats = translation_engine.get_cache_stats()
        logger.info(f"💾 Translation cache: {cache_stats['total_translations']} existing translations")
        logger.info(f"🤖 Mistral API: {'✅ Available' if cache_stats['mistral_api_available'] else '❌ Using fallback'}")
        
        translated_articles = await translation_engine.translate_articles_batch(
            english_articles, 
            category="News"
        )
        
        if not translated_articles:
            logger.error("❌ Translation failed!")
            return
        
        logger.info(f"✅ Translation completed: {len(translated_articles)} Ukrainian articles ready")
        
        # Step 3: Generate Ukrainian RSS
        logger.info("📡 Generating Ukrainian RSS feed...")
        await generate_ukrainian_rss(translated_articles)
        
        # Step 4: Final statistics
        final_stats = translation_engine.get_cache_stats()
        duration = datetime.now() - start_time
        
        logger.info(f"📊 Final statistics:")
        logger.info(f"   📰 Articles processed: {len(translated_articles)}")
        logger.info(f"   💾 Total cache entries: {final_stats['total_translations']}")
        logger.info(f"   🤖 Mistral API translations: {final_stats['mistral_api_translations']}")
        logger.info(f"   🧪 Fallback translations: {final_stats['mock_translations']}")
        logger.info(f"   ⏱️  Duration: {duration}")
        logger.info(f"   📄 Output file: {OUTPUT_FILE}")
        
        # Check output file size
        try:
            output_path = Path(OUTPUT_FILE)
            if output_path.exists():
                size_kb = output_path.stat().st_size / 1024
                logger.info(f"   📏 Feed size: {size_kb:.1f} KB")
        except Exception as e:
            logger.warning(f"⚠️ Could not check output file size: {e}")
        
        logger.info("🎉 Ukrainian Anthropic News RSS generation completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
        import traceback
        logger.debug(f"Full traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
