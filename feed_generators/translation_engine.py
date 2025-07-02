#!/usr/bin/env python3
"""
AI-PULSE Translation Engine - Ukrainian Language Support
Translates RSS feed content to Ukrainian using Claude API with caching
"""

import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional

# Setup logging
logger = logging.getLogger('ai-pulse-translation')

class TranslationEngine:
    """Handles translation of RSS content to Ukrainian using Claude API"""
    
    def __init__(self, cache_file: str = "cache/translations_cache.json"):
        """Initialize translation engine with cache
        
        Args:
            cache_file: Path to translation cache file
        """
        self.cache_file = Path(cache_file)
        self.cache_file.parent.mkdir(exist_ok=True)
        self.cache = self._load_cache()
        
    def _load_cache(self) -> Dict:
        """Load existing translation cache"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    logger.info(f"📚 Loaded {len(cache)} cached translations")
                    return cache
        except Exception as e:
            logger.warning(f"⚠️ Failed to load cache: {e}")
        
        return {}
    
    def _save_cache(self) -> None:
        """Save translation cache to disk"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
                logger.debug(f"💾 Saved {len(self.cache)} translations to cache")
        except Exception as e:
            logger.error(f"❌ Failed to save cache: {e}")
    
    def _generate_cache_key(self, title: str, description: str) -> str:
        """Generate unique cache key for content
        
        Args:
            title: Article title
            description: Article description
            
        Returns:
            MD5 hash of content as cache key
        """
        content = f"{title}|{description}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _create_translation_prompt(self, articles: List[Dict], category: str) -> str:
        """Create Claude prompt for translation
        
        Args:
            articles: List of articles to translate  
            category: Article category (News, Engineering, Alignment Science)
            
        Returns:
            Formatted prompt for Claude
        """
        category_context = {
            'News': 'новини та оголошення',
            'Engineering': 'технічні статті та інженерні рішення', 
            'Alignment Science': 'дослідження безпеки ШІ та alignment'
        }
        
        context = category_context.get(category, 'статті про штучний інтелект')
        
        prompt = f"""Переклади ці статті про ШІ на українську мову. Це {context} від Anthropic.

КРИТИЧНО ВАЖЛИВО:
- Зберігай технічну термінологію англійською: "Claude", "LLM", "alignment", "AI safety"
- Переклади акуратно, зберігаючи точний смысл
- Використовуй природну українську мову
- Зберігай стиль та тон оригіналу
- НЕ перекладай назви компаній та продуктів

Верни ТІЛЬКИ валідний JSON у форматі:
{{
  "translations": [
    {{
      "title": "переклад заголовка",
      "description": "переклад опису"
    }}
  ]
}}

Статті для перекладу:
"""
        
        for i, article in enumerate(articles, 1):
            prompt += f"""
{i}. Заголовок: {article['title']}
   Опис: {article['description']}
"""
        
        return prompt

    
    def _generate_mock_translations(self, articles: List[Dict], category: str) -> List[Dict]:
        """Generate mock translations for testing (CLI mode)
        
        Args:
            articles: Articles to translate
            category: Article category
            
        Returns:
            Mock translations in Ukrainian
        """
        logger.info("🧪 Generating mock Ukrainian translations for testing...")
        
        mock_translations = []
        
        # Ukrainian prefixes based on category
        category_prefixes = {
            'News': '[Новини]',
            'Engineering': '[Інженерія]', 
            'Alignment Science': '[Безпека ШІ]',
            'Announcements': '[Оголошення]',
            'Product': '[Продукт]',
            'Policy': '[Політика]'
        }
        
        # Common translations mapping
        title_translations = {
            'Introducing': 'Представляємо',
            'Claude': 'Claude',
            'Anthropic': 'Anthropic', 
            'AI Safety': 'Безпека ШІ',
            'Language Models': 'мовні моделі',
            'Large Language Models': 'великі мовні моделі',
            'raises': 'залучає',
            'Series E': 'Серія E',
            'valuation': 'оцінка',
            'board of directors': 'рада директорів',
            'appointed': 'призначений',
            'Safety Level': 'рівень безпеки',
            'Protections': 'захист',
            'National Security': 'національна безпека',
            'Best practices': 'найкращі практики',
            'Multi-agent': 'мульти-агентна',
            'Research system': 'дослідницька система',
            'Desktop Extensions': 'розширення для робочого столу',
            'One-click': 'в один клік',
            'Installation': 'встановлення'
        }
        
        description_templates = {
            'News': 'Останні новини від Anthropic: {}',
            'Engineering': 'Технічні розробки від Anthropic: {}', 
            'Alignment Science': 'Дослідження безпеки ШІ від Anthropic: {}',
            'Announcements': 'Оголошення від Anthropic: {}',
            'Product': 'Продуктові оновлення від Anthropic: {}',
            'Policy': 'Політичні рішення від Anthropic: {}'
        }
        
        for article in articles:
            # Mock translate title
            title = article['title']
            for en, ua in title_translations.items():
                title = title.replace(en, ua)
            
            # Add category prefix
            prefix = category_prefixes.get(article.get('category', category), '[Новини]')
            mock_title = f"{prefix} {title}"
            
            # Mock translate description  
            description_template = description_templates.get(article.get('category', category), 'Контент від Anthropic: {}')
            mock_description = description_template.format(title)
            
            mock_translations.append({
                'title': mock_title,
                'description': mock_description
            })
            
            logger.debug(f"🧪 Mock translation: {article['title'][:30]}... → {mock_title[:30]}...")
        
        return mock_translations
    
    async def translate_articles_batch(self, articles: List[Dict], category: str = "News") -> List[Dict]:
        """Translate multiple articles in batch for performance
        
        Args:
            articles: List of articles with 'title' and 'description'
            category: Article category for context
            
        Returns:
            List of articles with Ukrainian translations
        """
        if not articles:
            return []
            
        logger.info(f"🇺🇦 Translating {len(articles)} {category} articles to Ukrainian...")
        
        # Check cache and separate cached vs new articles
        cached_articles = []
        to_translate = []
        
        for article in articles:
            cache_key = self._generate_cache_key(article['title'], article['description'])
            
            if cache_key in self.cache:
                # Use cached translation
                cached_translation = self.cache[cache_key].copy()
                cached_translation.update(article)  # Keep original metadata
                cached_translation['title'] = self.cache[cache_key]['title']
                cached_translation['description'] = self.cache[cache_key]['description']
                cached_articles.append(cached_translation)
                logger.debug(f"📚 Using cached translation: {article['title'][:30]}...")
            else:
                to_translate.append(article)
        
        translated_articles = cached_articles.copy()
        
        # Translate new articles if any
        if to_translate:
            logger.info(f"🔄 Translating {len(to_translate)} new articles via Claude...")
            
            try:
                # Check if we're in browser environment (has window.claude.complete)
                try:
                    # Try to access window.claude.complete
                    if 'window' in globals() and hasattr(window, 'claude'):
                        # Production mode: Use Claude API
                        prompt = self._create_translation_prompt(to_translate, category)
                        response = await window.claude.complete(prompt)
                        translation_data = json.loads(response)
                        translations = translation_data.get('translations', [])
                    else:
                        raise NameError("window not available")
                        
                except NameError:
                    # CLI/Testing mode: Use mock translations
                    logger.warning("⚠️ Claude API not available - using mock translations for testing")
                    translations = self._generate_mock_translations(to_translate, category)
                
                if len(translations) != len(to_translate):
                    logger.warning(f"⚠️ Translation count mismatch: {len(translations)} vs {len(to_translate)}")
                
                # Process translations and update cache
                for i, (original, translation) in enumerate(zip(to_translate, translations)):
                    cache_key = self._generate_cache_key(original['title'], original['description'])
                    
                    # Cache the translation
                    self.cache[cache_key] = {
                        'title': translation['title'],
                        'description': translation['description'],
                        'translated_at': datetime.now(timezone.utc).isoformat()
                    }
                    
                    # Create translated article
                    translated_article = original.copy()
                    translated_article['title'] = translation['title']
                    translated_article['description'] = translation['description']
                    translated_articles.append(translated_article)
                    
                    logger.debug(f"✅ Translated: {original['title'][:30]}... → {translation['title'][:30]}...")
                
                # Save updated cache
                self._save_cache()
                logger.info(f"🎉 Successfully translated {len(translations)} articles!")
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse Claude response as JSON: {e}")
                # Return originals if translation fails
                translated_articles.extend(to_translate)
                
            except Exception as e:
                logger.error(f"❌ Translation failed: {e}")
                # Return originals if translation fails  
                translated_articles.extend(to_translate)
        
        logger.info(f"📝 Total articles prepared: {len(translated_articles)} ({len(cached_articles)} cached + {len(translations) if 'translations' in locals() else 0} new)")
        return translated_articles
    
    async def translate_single_article(self, title: str, description: str, category: str = "News") -> Tuple[str, str]:
        """Translate a single article
        
        Args:
            title: Article title
            description: Article description
            category: Article category
            
        Returns:
            Tuple of (translated_title, translated_description)
        """
        article = {'title': title, 'description': description}
        translated = await self.translate_articles_batch([article], category)
        
        if translated:
            return translated[0]['title'], translated[0]['description']
        else:
            logger.warning("⚠️ Translation failed, returning original text")
            return title, description
    
    def get_cache_stats(self) -> Dict:
        """Get translation cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            'total_translations': len(self.cache),
            'cache_file': str(self.cache_file),
            'cache_size_mb': self.cache_file.stat().st_size / 1024 / 1024 if self.cache_file.exists() else 0
        }


# Test function
async def test_translation_engine():
    """Test the translation engine with sample data"""
    engine = TranslationEngine()
    
    test_articles = [
        {
            'title': 'Introducing Claude 4',
            'description': 'Latest from Anthropic: Introducing Claude 4',
            'category': 'News'
        },
        {
            'title': 'Alignment Faking in Large Language Models', 
            'description': 'AI Safety research from Anthropic: Alignment Faking in Large Language Models',
            'category': 'Alignment Science'
        }
    ]
    
    translated = await engine.translate_articles_batch(test_articles, "News")
    
    for original, translated_article in zip(test_articles, translated):
        print(f"Original: {original['title']}")
        print(f"Ukrainian: {translated_article['title']}")
        print("---")


if __name__ == "__main__":
    import asyncio
    
    # Setup logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run test
    asyncio.run(test_translation_engine())
