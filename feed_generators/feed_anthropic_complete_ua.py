#!/usr/bin/env python3
"""
AI-PULSE Ukrainian Complete RSS Generator
Combines all English feeds and generates comprehensive Ukrainian translation
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
logger = logging.getLogger('anthropic-complete-ua')

# Configuration
ENGLISH_FEEDS = {
    "News": "feeds/feed_anthropic_news.xml",
    "Engineering": "feeds/feed_anthropic_engineering.xml", 
    "Alignment Science": "feeds/feed_anthropic_alignment.xml"
}
OUTPUT_FILE = "feeds/feed_anthropic_complete_ua.xml"
UKRAINIAN_FEED_TITLE = "Anthropic Повний Фід - AI-PULSE"
UKRAINIAN_FEED_DESCRIPTION = "Повний фід: новини, інженерія та дослідження безпеки ШІ від Anthropic (українською мовою)"
UKRAINIAN_FEED_LINK = "https://www.anthropic.com"

async def read_english_feeds() -> list:
    """Read and parse all English RSS feeds
    
    Returns:
        List of all articles from all English feeds with source labels
    """
    all_articles = []
    
    for source_name, feed_file in ENGLISH_FEEDS.items():
        feed_path = Path(feed_file)
        
        if not feed_path.exists():
            logger.warning(f"⚠️ English {source_name} feed not found: {feed_path}")
            continue
        
        try:
            tree = ET.parse(feed_path)
            root = tree.getroot()
            
            source_articles = []
            
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
                            'category': category_elem.text or source_name if category_elem is not None else source_name,
                            'pub_date': pub_date_elem.text or '' if pub_date_elem is not None else '',
                            'guid': guid_elem.text or '' if guid_elem is not None else '',
                            'source': source_name  # Add source label
                        }
                        source_articles.append(article)
                        
                except Exception as e:
                    logger.warning(f"⚠️ Failed to parse RSS item from {source_name}: {e}")
                    continue
            
            logger.info(f"📖 Read {len(source_articles)} articles from {source_name}")
            all_articles.extend(source_articles)
            
        except Exception as e:
            logger.error(f"❌ Failed to parse {source_name} feed: {e}")
            continue
    
    logger.info(f"📊 Total articles collected: {len(all_articles)} from all sources")
    return all_articles

async def generate_ukrainian_rss(articles: list) -> None:
    """Generate Ukrainian Complete RSS feed from translated articles
    
    Args:
        articles: List of translated articles from all sources
    """
    if not articles:
        logger.warning("⚠️ No articles to generate complete RSS feed")
        return
    
    try:
        # Create RSS feed generator
        fg = FeedGenerator()
        fg.title(UKRAINIAN_FEED_TITLE)
        fg.link(href=UKRAINIAN_FEED_LINK, rel='alternate')
        fg.description(UKRAINIAN_FEED_DESCRIPTION)
        fg.language('uk')  # Ukrainian language code
        fg.generator('AI-PULSE RSS Generator - Ukrainian Complete Translation')
        fg.docs('http://www.rssboard.org/rss-specification')
        fg.lastBuildDate(datetime.now(timezone.utc))
        
        # Sort articles by source for better organization
        news_articles = [a for a in articles if a.get('source') == 'News']
        engineering_articles = [a for a in articles if a.get('source') == 'Engineering']
        alignment_articles = [a for a in articles if a.get('source') == 'Alignment Science']
        
        # Add articles to feed in order: News, Engineering, Alignment Science
        for article_group in [news_articles, engineering_articles, alignment_articles]:
            for article in article_group:
                try:
                    fe = fg.add_entry()
                    
                    # Add source prefix to title for complete feed
                    source_prefixes = {
                        'News': '[Новини]',
                        'Engineering': '[Інженерія]',
                        'Alignment Science': '[Безпека ШІ]'
                    }
                    
                    source_prefix = source_prefixes.get(article.get('source', ''), '[Контент]')
                    if not article['title'].startswith('['):
                        title_with_source = f"{source_prefix} {article['title']}"
                    else:
                        title_with_source = article['title']
                    
                    fe.title(title_with_source)
                    fe.link(href=article['url'])
                    
                    # Add source info to description
                    description_with_source = f"{article['description']} (Джерело: {article.get('source', 'Unknown')})"
                    fe.description(description_with_source)
                    
                    fe.guid(article['guid'], permalink=False)
                    
                    # Add category properly
                    if 'category' in article and article['category']:
                        fe.category(term=article['category'])
                    
                    # Parse and set publication date
                    if article['pub_date']:
                        try:
                            pub_date = datetime.now(timezone.utc)
                            fe.pubDate(pub_date)
                        except:
                            fe.pubDate(datetime.now(timezone.utc))
                    else:
                        fe.pubDate(datetime.now(timezone.utc))
                        
                    logger.debug(f"➕ Added to complete RSS: {title_with_source[:50]}...")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to add article to complete RSS: {e}")
                    continue
        
        # Ensure output directory exists
        output_path = Path(OUTPUT_FILE)
        output_path.parent.mkdir(exist_ok=True)
        
        # Write RSS file
        rss_content = fg.rss_str(pretty=True)
        with open(output_path, 'wb') as f:
            f.write(rss_content)
        
        logger.info(f"✅ Ukrainian Complete RSS feed saved to: {output_path}")
        logger.info(f"📊 Complete feed contains {len(articles)} articles")
        
        # Log summary by source
        logger.info("📈 Summary by source:")
        for source in ['News', 'Engineering', 'Alignment Science']:
            count = len([a for a in articles if a.get('source') == source])
            logger.info(f"   {source}: {count} articles")
        
    except Exception as e:
        logger.error(f"❌ Failed to generate Ukrainian Complete RSS feed: {e}")
        raise

async def main():
    """Main function to generate Ukrainian complete RSS feed"""
    try:
        logger.info("🇺🇦 Starting Ukrainian Anthropic Complete RSS generation")
        
        # Step 1: Read all English feeds
        logger.info("📖 Reading all English RSS feeds...")
        english_articles = await read_english_feeds()
        
        if not english_articles:
            logger.error("❌ No English articles found in any feed!")
            return
        
        # Step 2: Translate to Ukrainian by source
        logger.info("🔄 Translating all articles to Ukrainian...")
        translation_engine = TranslationEngine()
        
        all_translated_articles = []
        
        # Translate each source separately for better context
        for source_name in ['News', 'Engineering', 'Alignment Science']:
            source_articles = [a for a in english_articles if a.get('source') == source_name]
            
            if source_articles:
                logger.info(f"🔄 Translating {len(source_articles)} {source_name} articles...")
                translated_source = await translation_engine.translate_articles_batch(
                    source_articles, 
                    category=source_name
                )
                all_translated_articles.extend(translated_source)
        
        if not all_translated_articles:
            logger.error("❌ Complete translation failed!")
            return
        
        # Step 3: Generate Ukrainian Complete RSS
        logger.info("📡 Generating Ukrainian Complete RSS feed...")
        await generate_ukrainian_rss(all_translated_articles)
        
        # Step 4: Display cache stats
        cache_stats = translation_engine.get_cache_stats()
        logger.info(f"📚 Translation cache: {cache_stats['total_translations']} entries")
        
        logger.info("🎉 Ukrainian Anthropic Complete RSS generation completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Complete generation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
