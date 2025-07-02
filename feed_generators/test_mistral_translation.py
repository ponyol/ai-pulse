#!/usr/bin/env python3
"""
Test script for Mistral-based translation engine
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from translation_engine import TranslationEngine

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_mistral_translations():
    """Test Mistral translation engine with sample data"""
    
    # Test articles from different categories
    test_articles = [
        {
            'title': 'Introducing Claude 4',
            'description': 'Latest from Anthropic: Introducing Claude 4, our most capable AI assistant yet with enhanced reasoning and safety features.',
            'category': 'News'
        },
        {
            'title': 'Alignment Faking in Large Language Models', 
            'description': 'AI Safety research from Anthropic: Alignment Faking in Large Language Models - how models might appear aligned while pursuing different goals.',
            'category': 'Alignment Science'
        },
        {
            'title': 'Building Scalable AI Systems',
            'description': 'Engineering insights from Anthropic: Building Scalable AI Systems with modern cloud architecture and distributed training.',
            'category': 'Engineering'
        }
    ]
    
    print("🔧 Testing Mistral Translation Engine")
    print(f"🔑 Mistral API Key: {'✅ Found' if os.getenv('MISTRAL_API_KEY') else '❌ Not found'}")
    print("=" * 60)
    
    # Initialize translation engine
    engine = TranslationEngine("cache/test_translations_cache.json")
    
    # Show cache stats
    stats = engine.get_cache_stats()
    print(f"📊 Cache Stats:")
    print(f"   Total translations: {stats['total_translations']}")
    print(f"   Mistral API translations: {stats['mistral_api_translations']}")
    print(f"   Mock translations: {stats['mock_translations']}")
    print(f"   Mistral API available: {stats['mistral_api_available']}")
    print()
    
    # Test each category
    for category in ['News', 'Engineering', 'Alignment Science']:
        category_articles = [a for a in test_articles if a['category'] == category]
        if not category_articles:
            continue
            
        print(f"🧪 Testing {category} translation...")
        
        try:
            translated = await engine.translate_articles_batch(category_articles, category)
            
            for original, translated_article in zip(category_articles, translated):
                print(f"📰 Original: {original['title']}")
                print(f"🇺🇦 Ukrainian: {translated_article['title']}")
                print(f"📝 Description: {translated_article['description'][:100]}...")
                print("-" * 40)
                
        except Exception as e:
            print(f"❌ Error testing {category}: {e}")
        
        print()
    
    # Test single article translation
    print("🧪 Testing single article translation...")
    try:
        title, description = await engine.translate_single_article(
            "Claude Desktop Extensions",
            "One-click installation and setup for Claude desktop integrations"
        )
        print(f"📰 Original: Claude Desktop Extensions")
        print(f"🇺🇦 Ukrainian: {title}")
        print(f"📝 Description: {description}")
    except Exception as e:
        print(f"❌ Error testing single translation: {e}")
    
    print()
    
    # Final cache stats
    final_stats = engine.get_cache_stats()
    print(f"📊 Final Cache Stats:")
    print(f"   Total translations: {final_stats['total_translations']}")
    print(f"   Mistral API translations: {final_stats['mistral_api_translations']}")
    print(f"   Mock translations: {final_stats['mock_translations']}")
    print(f"   Cache size: {final_stats['cache_size_mb']:.2f} MB")


if __name__ == "__main__":
    # Test with and without API key
    print("🚀 Starting Mistral Translation Tests")
    print()
    
    asyncio.run(test_mistral_translations())
    
    print("✅ Tests completed!")
