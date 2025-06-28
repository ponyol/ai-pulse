#!/usr/bin/env python3
"""
Anthropic Complete RSS Feed Generator
Combines all Anthropic sources into one comprehensive feed

This module aggregates content from:
- anthropic.com/news (main news and announcements)
- anthropic.com/engineering (technical blog posts)  
- alignment.anthropic.com (alignment science research)
- anthropic.com/research (research papers)

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
import feed_anthropic_news
import feed_anthropic_engineering  
import feed_anthropic_alignment

# Setup logging
logger = logging.getLogger('anthropic-complete')

# Configuration
OUTPUT_FILE = "feeds/feed_anthropic_complete.xml"

def collect_all_articles() -> list:
    """Collect articles from all Anthropic sources"""
    all_articles = []
    
    sources = [
        (feed_anthropic_news, 'News'),
        (feed_anthropic_engineering, 'Engineering'),
        (feed_anthropic_alignment, 'Alignment Science')
    ]
    
    for module, source_name in sources:
        try:
            logger.info(f"📰 Collecting from: {source_name}")
            
            # Get page content and extract articles
            if hasattr(module, 'get_page_content') and hasattr(module, 'extract_articles'):
                if source_name == 'News':
                    url = module.NEWS_URL
                elif source_name == 'Engineering':
                    url = module.ENGINEERING_URL
                else:  # Alignment
                    url = module.ALIGNMENT_URL
                    
                soup = module.get_page_content(url)
                articles = module.extract_articles(soup)
                
                # Add source information to each article
                for article in articles:
                    article['source'] = source_name
                    article['source_category'] = source_name
                
                all_articles.extend(articles)
                logger.info(f"✅ Collected {len(articles)} articles from {source_name}")
            
        except Exception as e:
            logger.error(f"❌ Error collecting from {source_name}: {e}")
            continue
    
    # Sort articles by publication date (most recent first)
    all_articles.sort(key=lambda x: x.get('pub_date', datetime.min.replace(tzinfo=timezone.utc)), 
                     reverse=True)
    
    logger.info(f"📊 Total collected: {len(all_articles)} articles from all sources")
    return all_articles

def generate_combined_rss_feed(articles: list) -> None:
    """Generate combined RSS feed from all sources"""
    logger.info("📡 Generating Complete Anthropic RSS feed...")
    
    # Create feed generator
    fg = FeedGenerator()
    fg.title('Anthropic Complete - AI-PULSE')
    fg.link(href='https://www.anthropic.com', rel='alternate')
    fg.description('Complete feed: News, Engineering, and Alignment Science from Anthropic')
    fg.language('en')
    fg.lastBuildDate(datetime.now(timezone.utc))
    fg.generator('AI-PULSE RSS Generator - Complete Feed')
    
    # Add articles to feed (limit to 100 for performance)
    for article in articles[:100]:
        fe = fg.add_entry()
        
        # Enhanced title with source prefix
        title_with_source = f"[{article.get('source', 'Anthropic')}] {article['title']}"
        fe.title(title_with_source)
        fe.link(href=article['url'])
        
        # Enhanced description with source information
        description = f"{article['description']} (Source: {article.get('source', 'Anthropic')})"
        fe.description(description)
        
        # Use source as category
        fe.category(term=article.get('source_category', article.get('category', 'Anthropic')))
        fe.pubDate(article['pub_date'])
        fe.guid(article['url'], False)
    
    # Ensure output directory exists
    output_path = Path(OUTPUT_FILE)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write RSS feed
    fg.rss_file(OUTPUT_FILE)
    logger.info(f"✅ Complete RSS feed saved to: {OUTPUT_FILE}")
    logger.info(f"📊 Combined feed contains {len(articles)} articles")

def main():
    """Main execution function"""
    try:
        logger.info("🚀 Starting Complete Anthropic RSS generation")
        
        # Collect articles from all sources
        all_articles = collect_all_articles()
        
        if not all_articles:
            logger.warning("⚠️  No articles collected from any source!")
            return
        
        # Generate combined RSS feed
        generate_combined_rss_feed(all_articles)
        
        logger.info("🎉 Complete Anthropic RSS generation completed!")
        
        # Summary by source
        sources_summary = {}
        for article in all_articles:
            source = article.get('source', 'Unknown')
            sources_summary[source] = sources_summary.get(source, 0) + 1
        
        logger.info("📈 Summary by source:")
        for source, count in sources_summary.items():
            logger.info(f"   {source}: {count} articles")
        
    except Exception as e:
        logger.error(f"💥 Fatal error in complete feed: {e}")
        raise

if __name__ == "__main__":
    main()
