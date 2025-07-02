#!/usr/bin/env python3
"""
AI-PULSE Ukrainian Mistral Changelog RSS Generator
Reads English Mistral changelog feed and generates Ukrainian translation
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
logger = logging.getLogger('mistral-changelog-ua')

# Configuration
ENGLISH_FEED_FILE = "feeds/feed_mistral_changelog.xml"
OUTPUT_FILE = "feeds/feed_mistral_changelog_ua.xml"
UKRAINIAN_FEED_TITLE = "Mistral AI API Changelog - AI-PULSE"
UKRAINIAN_FEED_DESCRIPTION = "Останні оновлення API, релізи моделей та технічні зміни від Mistral AI (українською мовою)"
UKRAINIAN_FEED_LINK = "https://docs.mistral.ai/getting-started/changelog"

async def read_english_feed() -> list:
    """Read and parse English RSS feed
    
    Returns:
        List of changelog entries from English feed
    """
    feed_path = Path(ENGLISH_FEED_FILE)
    
    if not feed_path.exists():
        logger.error(f"❌ English feed not found: {feed_path}")
        return []
    
    try:
        tree = ET.parse(feed_path)
        root = tree.getroot()
        
        entries = []
        
        # Parse RSS items
        for item in root.findall('.//item'):
            try:
                title_elem = item.find('title')
                description_elem = item.find('description')
                link_elem = item.find('link')
                pubdate_elem = item.find('pubDate')
                category_elem = item.find('category')
                
                if title_elem is not None and link_elem is not None:
                    entry = {
                        'title': title_elem.text or '',
                        'description': description_elem.text or '' if description_elem is not None else '',
                        'link': link_elem.text or '',
                        'pubdate': pubdate_elem.text or '' if pubdate_elem is not None else '',
                        'category': category_elem.text or 'API Update' if category_elem is not None else 'API Update'
                    }
                    entries.append(entry)
                    logger.debug(f"✅ Parsed entry: {entry['title'][:50]}...")
                    
            except Exception as e:
                logger.warning(f"⚠️ Error parsing RSS item: {e}")
                continue
        
        logger.info(f"📖 Read {len(entries)} entries from English feed")
        return entries
        
    except Exception as e:
        logger.error(f"❌ Failed to parse English feed: {e}")
        return []

async def translate_entries(entries: list) -> list:
    """Translate changelog entries to Ukrainian
    
    Args:
        entries: List of entries to translate
        
    Returns:
        List of translated entries
    """
    if not entries:
        logger.warning("⚠️ No entries to translate")
        return []
    
    logger.info(f"🌐 Starting translation of {len(entries)} changelog entries")
    
    # Initialize translation engine
    translator = TranslationEngine()
    
    # Translate entries in batches for efficiency
    translated_entries = await translator.translate_articles_batch(entries)
    
    logger.info(f"✅ Translation completed: {len(translated_entries)} entries")
    return translated_entries

async def create_ukrainian_feed(entries: list) -> None:
    """Create Ukrainian RSS feed from translated changelog entries
    
    Args:
        entries: List of translated entries
    """
    if not entries:
        logger.warning("⚠️ No entries to include in feed")
    
    # Create feed generator
    fg = FeedGenerator()
    fg.id(UKRAINIAN_FEED_LINK)
    fg.title(UKRAINIAN_FEED_TITLE)
    fg.link(href=UKRAINIAN_FEED_LINK, rel='alternate')
    fg.description(UKRAINIAN_FEED_DESCRIPTION)
    fg.author({'name': 'Mistral AI Docs (Ukrainian Translation)', 'email': 'support@mistral.ai'})
    fg.language('uk')  # Ukrainian language code
    fg.lastBuildDate(datetime.now(timezone.utc))
    fg.generator('AI-PULSE RSS Generator - Ukrainian Translation')
    fg.image(url='https://docs.mistral.ai/favicon.ico', title='Mistral AI Docs', link=UKRAINIAN_FEED_LINK)
    
    # Add entries to feed
    for entry in entries:
        try:
            fe = fg.add_entry()
            fe.id(entry['link'])
            fe.title(entry['title_ua'])
            fe.link(href=entry['link'])
            fe.description(entry['description_ua'])
            fe.category(term=entry['category_ua'])
            
            # Parse publication date
            if entry['pubdate']:
                try:
                    # Try to parse RFC 2822 format first
                    from email.utils import parsedate_to_datetime
                    pubdate = parsedate_to_datetime(entry['pubdate'])
                    fe.pubDate(pubdate)
                except:
                    # Fallback to current time if parsing fails
                    fe.pubDate(datetime.now(timezone.utc))
            else:
                fe.pubDate(datetime.now(timezone.utc))
                
        except Exception as e:
            logger.warning(f"⚠️ Error adding entry to feed: {e}")
            continue
    
    # Ensure output directory exists
    output_path = Path(OUTPUT_FILE)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write feed
    try:
        rss_str = fg.rss_str(pretty=True)
        with open(output_path, 'wb') as f:
            f.write(rss_str)
        
        logger.info(f"✅ Ukrainian RSS feed created: {output_path} ({len(entries)} entries)")
        
    except Exception as e:
        logger.error(f"❌ Failed to write Ukrainian feed: {e}")
        raise

async def main():
    """Main execution function"""
    try:
        logger.info("🚀 Starting Ukrainian Mistral Changelog RSS generation")
        
        # Step 1: Read English feed
        logger.info("📖 Reading English feed...")
        entries = await read_english_feed()
        
        if not entries:
            logger.error("❌ No entries found in English feed")
            return
        
        # Step 2: Translate entries
        logger.info("🌐 Translating entries to Ukrainian...")
        translated_entries = await translate_entries(entries)
        
        if not translated_entries:
            logger.error("❌ Translation failed")
            return
        
        # Step 3: Create Ukrainian feed
        logger.info("📝 Creating Ukrainian RSS feed...")
        await create_ukrainian_feed(translated_entries)
        
        logger.info("✅ Ukrainian Mistral Changelog RSS generation completed successfully!")
        
        # Print summary
        logger.info("📋 Generated feed summary:")
        logger.info(f"  📰 Total entries: {len(translated_entries)}")
        if translated_entries:
            logger.info("  🔤 Latest entries (Ukrainian):")
            for entry in translated_entries[:3]:
                logger.info(f"    - {entry['title_ua']}")
        
    except Exception as e:
        logger.error(f"❌ Error in Ukrainian RSS generation: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
