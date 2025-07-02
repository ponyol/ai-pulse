#!/usr/bin/env python3
"""
AI-PULSE Translation Engine - Ukrainian Language Support
Translates RSS feed content to Ukrainian using Mistral API with caching
"""

import os
import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional

# Setup logging
logger = logging.getLogger('ai-pulse-translation')

class TranslationEngine:
    """Handles translation of RSS content to Ukrainian using Mistral API"""
    
    def __init__(self, cache_file: str = "cache/translations_cache.json"):
        """Initialize translation engine with cache
        
        Args:
            cache_file: Path to translation cache file
        """
        self.cache_file = Path(cache_file)
        self.cache_file.parent.mkdir(exist_ok=True)
        self.cache = self._load_cache()
        
        # Mistral API configuration
        self.mistral_api_key = os.getenv('MISTRAL_API_KEY')
        self.mistral_base_url = "https://api.mistral.ai/v1/chat/completions"
        self.mistral_model = "mistral-large-latest"  # Best for translation quality
        
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
    
    def _create_mistral_prompt(self, articles: List[Dict], category: str) -> str:
        """Create Mistral prompt for translation
        
        Args:
            articles: List of articles to translate  
            category: Article category (News, Engineering, Alignment Science)
            
        Returns:
            Formatted prompt for Mistral
        """
        category_context = {
            'News': 'новини та оголошення',
            'Engineering': 'технічні статті та інженерні рішення', 
            'Alignment Science': 'дослідження безпеки ШІ та alignment'
        }
        
        context = category_context.get(category, 'статті про штучний інтелект')
        
        prompt = f"""Переклади ці статті про ШІ на українську мову. Це {context} від Anthropic.

КРИТИЧНО ВАЖЛИВО:
- Зберігай технічну термінологію англійською: "Claude", "LLM", "alignment", "AI safety", "Anthropic"
- Переклади акуратно, зберігаючи точний смысл та контекст
- Використовуй природну сучасну українську мову
- Зберігай професійний стиль та тон оригіналу
- НЕ перекладай назви компаній, продуктів та технічних термінів

Верни ТІЛЬКИ валідний JSON у точному форматі:
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

    async def _call_mistral_api(self, prompt: str) -> List[Dict]:
        """Call Mistral API for translation
        
        Args:
            prompt: Translation prompt
            
        Returns:
            List of translations
        """
        if not self.mistral_api_key:
            logger.warning("⚠️ MISTRAL_API_KEY not found, falling back to mock translations")
            return None
            
        logger.info(f"🌐 Calling Mistral AI API ({self.mistral_model})...")
        
        headers = {
            "Authorization": f"Bearer {self.mistral_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.mistral_model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,  # Low temperature for consistent translations
            "max_tokens": 4000,  # Enough for batch translations
            "top_p": 0.9
        }
        
        try:
            import aiohttp
            
            logger.debug(f"📡 Sending request to {self.mistral_base_url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.mistral_base_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result['choices'][0]['message']['content']
                        
                        # Log API usage stats
                        usage = result.get('usage', {})
                        if usage:
                            prompt_tokens = usage.get('prompt_tokens', 0)
                            completion_tokens = usage.get('completion_tokens', 0)
                            total_tokens = usage.get('total_tokens', 0)
                            logger.info(f"📊 Mistral API usage: {total_tokens} tokens ({prompt_tokens} prompt + {completion_tokens} completion)")
                        
                        # Parse JSON response
                        translation_data = json.loads(content)
                        translations = translation_data.get('translations', [])
                        
                        logger.info(f"✅ Mistral API success: Received {len(translations)} high-quality translations")
                        return translations
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Mistral API error {response.status}: {error_text}")
                        return None
                        
        except ImportError:
            logger.warning("⚠️ aiohttp not available, using requests...")
            # Fallback to sync requests
            import requests
            
            logger.debug(f"📡 Sending request to {self.mistral_base_url} (sync)")
            
            response = requests.post(self.mistral_base_url, headers=headers, json=payload)
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Log API usage stats
                usage = result.get('usage', {})
                if usage:
                    prompt_tokens = usage.get('prompt_tokens', 0)
                    completion_tokens = usage.get('completion_tokens', 0)
                    total_tokens = usage.get('total_tokens', 0)
                    logger.info(f"📊 Mistral API usage: {total_tokens} tokens ({prompt_tokens} prompt + {completion_tokens} completion)")
                
                translation_data = json.loads(content)
                translations = translation_data.get('translations', [])
                logger.info(f"✅ Mistral API success: Received {len(translations)} high-quality translations")
                return translations
            else:
                logger.error(f"❌ Mistral API error {response.status_code}: {response.text}")
                return None
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse Mistral response as JSON: {e}")
            logger.debug(f"Raw response content: {content[:200]}...")
            return None
            
        except Exception as e:
            logger.error(f"❌ Mistral API call failed: {e}")
            return None
    
    def _generate_mock_translations(self, articles: List[Dict], category: str) -> List[Dict]:
        """Generate mock translations for testing (CLI mode)
        
        Args:
            articles: Articles to translate
            category: Article category
            
        Returns:
            Mock translations in Ukrainian
        """
        logger.info(f"🧪 Generating rule-based Ukrainian translations for {len(articles)} {category} articles...")
        
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
        
        successful_translations = 0
        
        for article in articles:
            # Mock translate title
            title = article['title']
            original_title = title
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
            
            successful_translations += 1
            logger.debug(f"🧪 Rule-based: {original_title[:30]}... → {mock_title[:30]}...")
        
        logger.info(f"✅ Rule-based translations completed: {successful_translations}/{len(articles)} articles")
        logger.info(f"📝 Translation method: Dictionary-based with {len(title_translations)} term mappings")
        
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
            
        logger.info(f"🇺🇦 Translating {len(articles)} {category} articles to Ukrainian via Mistral...")
        
        # Check Mistral API availability
        if self.mistral_api_key:
            logger.info(f"🤖 Mistral API: ✅ Available (using {self.mistral_model})")
        else:
            logger.warning(f"⚠️ Mistral API: ❌ MISTRAL_API_KEY not found - using fallback translations")
        
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
        
        # Log cache efficiency
        if cached_articles:
            logger.info(f"💾 Cache hit: {len(cached_articles)}/{len(articles)} articles (efficiency: {len(cached_articles)/len(articles)*100:.1f}%)")
        
        # Translate new articles if any
        if to_translate:
            logger.info(f"🔄 Need to translate {len(to_translate)} new articles...")
            
            # Create prompt and call Mistral API
            prompt = self._create_mistral_prompt(to_translate, category)
            translations = await self._call_mistral_api(prompt)
            
            # Fallback to mock translations if Mistral API fails
            if translations is None:
                logger.warning("⚠️ Mistral API failed - falling back to rule-based translations")
                translations = self._generate_mock_translations(to_translate, category)
                translation_method = "fallback"
            else:
                logger.info(f"✅ Mistral API success: Received {len(translations)} translations")
                translation_method = "mistral_api"
            
            if len(translations) != len(to_translate):
                logger.warning(f"⚠️ Translation count mismatch: {len(translations)} vs {len(to_translate)}")
                # Pad with mock translations if needed
                while len(translations) < len(to_translate):
                    mock_translations = self._generate_mock_translations(to_translate[len(translations):], category)
                    translations.extend(mock_translations)
            
            # Process translations and update cache
            for i, (original, translation) in enumerate(zip(to_translate, translations)):
                cache_key = self._generate_cache_key(original['title'], original['description'])
                
                # Cache the translation
                self.cache[cache_key] = {
                    'title': translation['title'],
                    'description': translation['description'],
                    'translated_at': datetime.now(timezone.utc).isoformat(),
                    'translation_method': translation_method
                }
                
                # Create translated article
                translated_article = original.copy()
                translated_article['title'] = translation['title']
                translated_article['description'] = translation['description']
                translated_articles.append(translated_article)
                
                logger.debug(f"✅ Translated: {original['title'][:30]}... → {translation['title'][:30]}...")
            
            # Save updated cache
            self._save_cache()
            api_method = "Mistral API" if translation_method == "mistral_api" else "Rule-based fallback"
            logger.info(f"🎉 Successfully translated {len(translations)} articles via {api_method}!")
        
        # Final summary with detailed stats
        total_articles = len(translated_articles)
        cached_count = len(cached_articles)
        new_count = len(translations) if 'translations' in locals() else 0
        
        logger.info(f"📝 Ukrainian feed ready: {total_articles} articles total")
        logger.info(f"   💾 Cached: {cached_count} articles")
        logger.info(f"   🆕 New: {new_count} articles")
        
        if new_count > 0:
            method = "Mistral API" if self.mistral_api_key and translations else "Fallback"
            logger.info(f"   🤖 Translation method: {method}")
        
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
        mistral_count = sum(1 for v in self.cache.values() if v.get('translation_method') == 'mistral_api')
        mock_count = sum(1 for v in self.cache.values() if v.get('translation_method') == 'mock')
        
        return {
            'total_translations': len(self.cache),
            'mistral_api_translations': mistral_count,
            'mock_translations': mock_count,
            'cache_file': str(self.cache_file),
            'cache_size_mb': self.cache_file.stat().st_size / 1024 / 1024 if self.cache_file.exists() else 0,
            'mistral_api_available': bool(self.mistral_api_key)
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
