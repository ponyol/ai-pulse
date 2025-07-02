#!/usr/bin/env python3
"""
Mistral AI Complete RSS Feed Generator
Combines all Mistral AI sources into one comprehensive feed

This module aggregates content from:
- mistral.ai/news (main news and product announcements)
- docs.mistral.ai/changelog (API updates and technical changes)

Author: AI-PULSE Project
"""

import sys
import os
import logging
from datetime import datetime, timezone
from pathlib import Path
from feedgen.feed import FeedGenerator

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Import other feed generators
import feed_mistral_news
import feed_mistral_changelog

# Setup logging
logger = logging.getLogger('mistral-complete')

# Configuration
OUTPUT_FILE = "feeds/feed_mistral_complete.xml"

def collect_all_articles() -> list:
    """Collect articles from all Mistral AI sources"""
    all_articles = []
    
    sources = [
        (feed_mistral_news, 'News'),
        (feed_mistral_changelog, 'Changelog')
    ]
    
    for module, source_name in sources:
        try:
            logger.info(f"📰 Collecting from: {source_name}")
            
            # Get page content and extract articles
            if hasattr(module, 'get_page_content') and hasattr(module, 'extract_articles'):
                # For news module
                soup = module.get_page_content(module.NEWS_URL if hasattr(module, 'NEWS_URL') else module.CHANGELOG_URL)
                if hasattr(module, 'extract_articles'):
                    articles = module.extract_articles(soup)
                else:
                    articles = module.extract_changelog_entries(soup)
            elif hasattr(module, 'extract_changelog_entries'):
                # For changelog module
                soup = module.get_page_content(module.CHANGELOG_URL)
                articles = module.extract_changelog_entries(soup)
            else:
                logger.warning(f"⚠️ Unknown module interface for {source_name}")
                continue
            
            # Add source tag to each article
            for article in articles:
                article['source'] = source_name
                article['source_category'] = source_name
            
            all_articles.extend(articles)
            logger.info(f"✅ Added {len(articles)} articles from {source_name}")
            
        except Exception as e:
            logger.error(f"❌ Error collecting from {source_name}: {e}")
            continue
    
    # Sort by date (newest first)
    all_articles.sort(key=lambda x: x.get('date', datetime.now(timezone.utc)), reverse=True)
    
    logger.info(f"📋 Total articles collected: {len(all_articles)}")
    return all_articles

def create_complete_feed(articles: list) -> None:
    """Create comprehensive RSS feed from all articles"""
    if not articles:
        logger.warning("No articles found, creating empty feed")
    
    # Create feed
    fg = FeedGenerator()
    fg.id("https://mistral.ai/")
    fg.title("Mistral AI Complete Feed - AI-PULSE")
    fg.link(href="https://mistral.ai/", rel='alternate')
    fg.description("Comprehensive coverage of Mistral AI: news, product announcements, API updates, and technical changes")
    fg.author({'name': 'Mistral AI (Aggregated)', 'email': 'contact@mistral.ai'})
    fg.language('en')
    fg.lastBuildDate(datetime.now(timezone.utc))
    fg.generator('AI-PULSE RSS Generator - Complete Feed')
    fg.image(url='https://mistral.ai/favicon.ico', title='Mistral AI Complete', link='https://mistral.ai/')
    
    # Add articles to feed
    for article in articles:
        try:
            fe = fg.add_entry()
            fe.id(article['url'])
            
            # Add source prefix to title for clarity
            source_prefix = f"[{article.get('source', 'Mistral')}] "
            title = article['title']
            if not title.startswith('['):
                title = source_prefix + title
            
            fe.title(title)
            fe.link(href=article['url'])
            
            # Enhanced description with source info
            description = article.get('description', article['title'])
            if article.get('source'):
                description = f"Source: {article['source']}\n\n{description}"
            
            fe.description(description)
            fe.pubDate(article['date'])
            
            # Use source-specific category or fallback
            category = article.get('category', article.get('source', 'Mistral AI'))
            fe.category(term=category)
            
            # Add enclosure for images if available
            if article.get('image'):
                try:
                    fe.enclosure(article['image'], '0', 'image/jpeg')
                except:
                    pass  # Skip if enclosure fails
                    
        except Exception as e:
            logger.warning(f"⚠️ Error adding article to feed: {e}")
            continue
    
    # Ensure output directory exists
    output_path = Path(OUTPUT_FILE)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write feed
    rss_str = fg.rss_str(pretty=True)
    with open(output_path, 'wb') as f:
        f.write(rss_str)
    
    logger.info(f"✅ Complete RSS feed created: {output_path} ({len(articles)} articles)")

def main():
    """Main execution function"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        logger.info("🚀 Starting Mistral AI Complete RSS generation")
        
        # Collect articles from all sources
        articles = collect_all_articles()
        
        # Create complete feed
        create_complete_feed(articles)
        
        logger.info(f"✅ Successfully generated complete RSS feed with {len(articles)} total articles")
        
        # Print summary by source
        if articles:
            logger.info("📋 Summary by source:")
            source_counts = {}
            for article in articles:
                source = article.get('source', 'Unknown')
                source_counts[source] = source_counts.get(source, 0) + 1
            
            for source, count in source_counts.items():
                logger.info(f"  {source}: {count} articles")
            
            logger.info("🔝 Latest articles:")
            for article in articles[:5]:
                source = article.get('source', 'Unknown')
                logger.info(f"  [{source}] {article['title']}")
        
    except Exception as e:
        logger.error(f"❌ Error generating complete RSS feed: {e}")
        raise

if __name__ == "__main__":
    main()
