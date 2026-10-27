from __future__ import annotations

from functools import lru_cache


@lru_cache(maxsize=512)
def translate_to_french(text: str) -> str:
    text = (text or '').strip()
    if not text:
        return ''
    try:
        from deep_translator import GoogleTranslator
        return GoogleTranslator(source='auto', target='fr').translate(text)
    except Exception:
        return text
