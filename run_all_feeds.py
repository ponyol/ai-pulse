#!/usr/bin/env python3
"""
AI-PULSE RSS Feed Generator
Main script to run all Anthropic feed generators

This script coordinates the generation of RSS feeds from multiple Anthropic sources:
- anthropic.com/news (main news and announcements)
- anthropic.com/engineering (technical blog posts)  
- alignment.anthropic.com (alignment science research)
- anthropic.com/research (research papers)

Author: AI-PULSE Project
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Add feed_generators to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'feed_generators'))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ai-pulse')

def main():
    """Run all RSS feed generators"""
    start_time = datetime.now()
    logger.info("🚀 AI-PULSE RSS generation started")
    
    # Ensure feeds directory exists
    feeds_dir = Path('feeds')
    feeds_dir.mkdir(exist_ok=True)
    
    # List of generators to run
    generators = [
        ('feed_anthropic_news', 'Anthropic News'),
        ('feed_anthropic_engineering', 'Anthropic Engineering'),
        ('feed_anthropic_alignment', 'Anthropic Alignment'),
        ('feed_anthropic_complete', 'Complete Feed (Combined)')
    ]
    
    success_count = 0
    total_count = len(generators)
    
    for module_name, description in generators:
        try:
            logger.info(f"📰 Generating: {description}")
            
            # Dynamic import
            module = __import__(module_name)
            
            # Run the generator
            if hasattr(module, 'main'):
                module.main()
                logger.info(f"✅ {description} - Success")
                success_count += 1
            else:
                logger.error(f"❌ {description} - No main() function found")
                
        except ImportError as e:
            logger.error(f"❌ {description} - Import error: {e}")
        except Exception as e:
            logger.error(f"❌ {description} - Error: {e}")
    
    # Final summary
    duration = datetime.now() - start_time
    logger.info(f"🏁 AI-PULSE generation completed")
    logger.info(f"📊 Success: {success_count}/{total_count} feeds")
    logger.info(f"⏱️  Duration: {duration}")
    
    if success_count == 0:
        logger.error("🚨 No feeds generated successfully!")
        sys.exit(1)
    elif success_count < total_count:
        logger.warning(f"⚠️  Only {success_count}/{total_count} feeds generated")
        sys.exit(1)
    else:
        logger.info("🎉 All feeds generated successfully!")

if __name__ == "__main__":
    main()
