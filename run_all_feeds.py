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
    
    # Check Mistral API availability
    mistral_key = os.getenv('MISTRAL_API_KEY')
    logger.info(f"🤖 Mistral API: {'✅ Available' if mistral_key else '❌ Not found (using fallback)'}")
    
    # Ensure feeds directory exists
    feeds_dir = Path('feeds')
    feeds_dir.mkdir(exist_ok=True)
    
    # List of generators to run - ENGLISH FIRST, then Ukrainian
    generators = [
        # Anthropic English feeds - MUST run first
        ('feed_anthropic_news', 'Anthropic News'),
        ('feed_anthropic_engineering', 'Anthropic Engineering'),
        ('feed_anthropic_alignment', 'Anthropic Alignment'),
        ('feed_anthropic_complete', 'Anthropic Complete Feed'),
        
        # Mistral English feeds - MUST run first
        ('feed_mistral_news', 'Mistral AI News'),
        ('feed_mistral_changelog', 'Mistral AI Changelog'),
        ('feed_mistral_complete', 'Mistral AI Complete Feed'),
        
        # Anthropic Ukrainian feeds - run after English feeds are ready
        ('feed_anthropic_news_ua', 'Anthropic News (Ukrainian)'),
        ('feed_anthropic_engineering_ua', 'Anthropic Engineering (Ukrainian)'),
        ('feed_anthropic_alignment_ua', 'Anthropic Alignment (Ukrainian)'),
        ('feed_anthropic_complete_ua', 'Anthropic Complete Feed (Ukrainian)'),
        
        # Mistral Ukrainian feeds - run after English feeds are ready
        ('feed_mistral_news_ua', 'Mistral AI News (Ukrainian)'),
        ('feed_mistral_changelog_ua', 'Mistral AI Changelog (Ukrainian)'),
        ('feed_mistral_complete_ua', 'Mistral AI Complete Feed (Ukrainian)')
    ]
    
    success_count = 0
    total_count = len(generators)
    english_feeds_count = 7  # 4 Anthropic + 3 Mistral
    ukrainian_feeds_count = 7  # 4 Anthropic + 3 Mistral
    
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
                
                logger.info(f"🔄 Starting Ukrainian translation process...")
                
                # Run Ukrainian generator as subprocess since they use asyncio
                result = subprocess.run([
                    sys.executable, f"feed_generators/{module_name}.py"
                ], capture_output=True, text=True, cwd=".")
                
                if result.returncode == 0:
                    logger.info(f"✅ {description} - Success")
                    
                    # Parse and display key metrics from stdout
                    # Combine stdout and stderr since Ukrainian generators log to stderr
                    all_output = (result.stdout + result.stderr).strip()
                    output_lines = all_output.split('\n') if all_output else []
                    metrics_found = False
                    
                    for line in output_lines:
                        # Extract log message content (after timestamp and logger name)
                        if ' - ' in line and ' - INFO - ' in line:
                            message = line.split(' - INFO - ')[-1]
                        else:
                            message = line
                        
                        # Show key translation metrics
                        if 'mistral api:' in message.lower():
                            logger.info(f"   🤖 {message}")
                            metrics_found = True
                        elif 'cache hit:' in message.lower():
                            logger.info(f"   💾 {message}")
                            metrics_found = True
                        elif 'articles processed:' in message.lower():
                            logger.info(f"   📰 {message}")
                            metrics_found = True
                        elif 'mistral api translations:' in message.lower():
                            logger.info(f"   🔗 {message}")
                            metrics_found = True
                        elif 'fallback translations:' in message.lower():
                            logger.info(f"   🧪 {message}")
                            metrics_found = True
                        elif 'duration:' in message.lower():
                            logger.info(f"   ⏱️ {message}")
                            metrics_found = True
                        elif 'feed size:' in message.lower():
                            logger.info(f"   📏 {message}")
                            metrics_found = True
                    
                    if not metrics_found:
                        # Fallback: show that Ukrainian translation completed
                        logger.info(f"   🇺🇦 Ukrainian translation completed")
                    
                    success_count += 1
                else:
                    logger.error(f"❌ {description} - Error (exit code: {result.returncode})")
                    if result.stderr:
                        # Show detailed error info
                        stderr_lines = result.stderr.strip().split('\n')
                        for line in stderr_lines[-3:]:  # Show last 3 error lines
                            if line.strip():
                                logger.error(f"   💥 {line}")
                    if result.stdout:
                        # Show any stdout that might contain useful info
                        stdout_lines = result.stdout.strip().split('\n')
                        for line in stdout_lines[-2:]:  # Show last 2 output lines
                            if line.strip() and 'error' in line.lower():
                                logger.error(f"   📋 {line}")
                    
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
        
        # Check generated feed sizes
        try:
            feed_files = list(Path('feeds').glob('*.xml'))
            logger.info(f"📂 Generated {len(feed_files)} RSS files:")
            for feed_file in sorted(feed_files):
                size_kb = feed_file.stat().st_size / 1024
                logger.info(f"   📄 {feed_file.name}: {size_kb:.1f} KB")
        except Exception as e:
            logger.warning(f"⚠️ Could not check feed file sizes: {e}")


if __name__ == "__main__":
    main()
