"""
Simple translation system for backend API messages
"""
import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

class Translator:
    """Simple translator for backend error messages"""
    
    def __init__(self):
        self._translations: Dict[str, Dict[str, Any]] = {}
        self._default_locale = "en"
        self._load_translations()
    
    def _load_translations(self):
        """Load all translation files"""
        locales_dir = Path(__file__).parent / "locales"
        
        for locale_file in locales_dir.glob("*.json"):
            locale = locale_file.stem
            try:
                with open(locale_file, 'r', encoding='utf-8') as f:
                    self._translations[locale] = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load translations for {locale}: {e}")
    
    def translate(self, key: str, locale: str = None, **kwargs) -> str:
        """
        Translate a key to the specified locale with parameter substitution
        
        Args:
            key: Translation key in dot notation (e.g., 'errors.calendar_not_found')
            locale: Target locale (defaults to 'en')
            **kwargs: Parameters for string formatting
            
        Returns:
            Translated string with parameters substituted
        """
        if locale is None:
            locale = self._default_locale
            
        # Fall back to English if locale not available
        if locale not in self._translations:
            locale = self._default_locale
            
        # Get translation data
        translation_data = self._translations.get(locale, {})
        
        # Navigate through nested dictionary using dot notation
        keys = key.split('.')
        result = translation_data
        
        for k in keys:
            if isinstance(result, dict) and k in result:
                result = result[k]
            else:
                # Fallback to English if key not found
                if locale != self._default_locale:
                    return self.translate(key, self._default_locale, **kwargs)
                # If still not found, return the key itself
                return key
        
        # If result is not a string, return the key
        if not isinstance(result, str):
            return key
            
        # Format string with provided parameters
        try:
            return result.format(**kwargs)
        except (KeyError, ValueError):
            # If formatting fails, return the unformatted string
            return result
    
    def t(self, key: str, locale: str = None, **kwargs) -> str:
        """Shorthand for translate method"""
        return self.translate(key, locale, **kwargs)

# Global translator instance
translator = Translator()

def get_translator() -> Translator:
    """Get the global translator instance"""
    return translator

def t(key: str, locale: str = None, **kwargs) -> str:
    """Global translation function"""
    return translator.translate(key, locale, **kwargs)