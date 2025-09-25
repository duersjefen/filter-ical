"""
Utilities for internationalization
"""
from typing import Optional
from fastapi import Request

def get_locale_from_request(request: Request) -> str:
    """
    Extract locale from request headers
    
    Args:
        request: FastAPI request object
        
    Returns:
        Locale string (defaults to 'en')
    """
    # Check Accept-Language header
    accept_language = request.headers.get('accept-language')
    if accept_language:
        # Parse the first language preference
        # Format: "en-US,en;q=0.9,de;q=0.8"
        languages = accept_language.split(',')
        if languages:
            primary_lang = languages[0].strip()
            # Extract just the language part (before any '-' or ';')
            lang_code = primary_lang.split('-')[0].split(';')[0].strip()
            
            # Support only specific languages we have translations for
            if lang_code.lower() in ['en', 'de']:
                return lang_code.lower()
    
    # Default to English
    return 'en'

def format_error_message(key: str, locale: str = 'en', **kwargs) -> str:
    """
    Format an error message using the translation system
    
    Args:
        key: Translation key (e.g., 'calendar_not_found')  
        locale: Target locale
        **kwargs: Parameters for string formatting
        
    Returns:
        Formatted error message
    """
    from .translator import t
    return t(f"errors.{key}", locale, **kwargs)