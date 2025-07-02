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
    """Run all RSS feed generators (English + Ukrainian)"""
    start_time = datetime.now()
    logger.info("🚀 AI-PULSE RSS generation started")
    
    # Ensure feeds directory exists
    feeds_dir = Path('feeds')
    feeds_dir.mkdir(exist_ok=True)
    
    # List of generators to run - ENGLISH FIRST, then Ukrainian
    generators = [
        # English feeds (existing) - MUST run first
        ('feed_anthropic_news', 'Anthropic News'),
        ('feed_anthropic_engineering', 'Anthropic Engineering'),
        ('feed_anthropic_alignment', 'Anthropic Alignment'),
        ('feed_anthropic_complete', 'Complete Feed (Combined)'),
        
        # Ukrainian feeds (new) - run after English feeds are ready
        ('feed_anthropic_news_ua', 'Anthropic News (Ukrainian)'),
        ('feed_anthropic_engineering_ua', 'Anthropic Engineering (Ukrainian)'),
        ('feed_anthropic_alignment_ua', 'Anthropic Alignment (Ukrainian)'),
        ('feed_anthropic_complete_ua', 'Complete Feed (Ukrainian)')
    ]
    
    success_count = 0
    total_count = len(generators)
    english_feeds_count = 4
    ukrainian_feeds_count = 4
    
    logger.info(f"📊 Total feeds to generate: {total_count} ({english_feeds_count} English + {ukrainian_feeds_count} Ukrainian)")
    
    for i, (module_name, description) in enumerate(generators, 1):
        try:
            is_ukrainian = module_name.endswith('_ua')
            emoji = "🇺🇦" if is_ukrainian else "🇬🇧"
            
            logger.info(f"{emoji} [{i}/{total_count}] Generating: {description}")
            
            # Dynamic import with proper path handling
            if is_ukrainian:
                # Ukrainian generators need async execution
                import subprocess
                import sys
                
                # Run Ukrainian generator as subprocess since they use asyncio
                result = subprocess.run([
                    sys.executable, f"feed_generators/{module_name}.py"
                ], capture_output=True, text=True, cwd=".")
                
                if result.returncode == 0:
                    logger.info(f"✅ {description} - Success")
                    success_count += 1
                else:
                    logger.error(f"❌ {description} - Error: {result.stderr}")
                    
            else:
                # English generators - direct import
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
    
    # More detailed success analysis
    if success_count == 0:
        logger.error("🚨 No feeds generated successfully!")
        sys.exit(1)
    elif success_count < english_feeds_count:
        logger.error(f"🚨 English feeds incomplete: {success_count} vs {english_feeds_count} expected")
        sys.exit(1)
    elif success_count < total_count:
        english_success = min(success_count, english_feeds_count)
        ukrainian_success = max(0, success_count - english_feeds_count)
        
        logger.warning(f"⚠️  Partial success: {english_success}/{english_feeds_count} English + {ukrainian_success}/{ukrainian_feeds_count} Ukrainian")
        
        if english_success == english_feeds_count:
            logger.info("✅ All English feeds generated successfully")
            if ukrainian_success > 0:
                logger.info(f"🇺🇦 {ukrainian_success} Ukrainian feeds generated")
        
        sys.exit(1)
    else:
        logger.info("🎉 All feeds generated successfully!")
        logger.info(f"🇬🇧 English feeds: {english_feeds_count}")
        logger.info(f"🇺🇦 Ukrainian feeds: {ukrainian_feeds_count}")
        logger.info("📡 RSS feeds available in feeds/ directory")
if __name__ == "__main__":
    main()
