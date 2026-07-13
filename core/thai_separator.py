import re
import logging
from typing import List, Tuple

logger = logging.getLogger("Engine.ThaiSeparator")

def is_thai_char(char: str) -> bool:
    """Check if a character is in the Thai Unicode range."""
    return '\u0e00' <= char <= '\u0e7f'

def contains_thai(text: str) -> bool:
    """Check if the string contains any Thai characters."""
    return any(is_thai_char(c) for c in text)

def split_thai_and_non_thai(text: str) -> List[Tuple[str, bool]]:
    """
    Splits text into chunks of Thai and non-Thai characters.
    Returns a list of tuples: (chunk_text, is_thai)
    """
    if not text:
        return []
        
    # Split by sequence of Thai characters, keeping the delimiters in the result
    chunks = re.split(r'([\u0e00-\u0e7f]+)', text)
    
    result = []
    for chunk in chunks:
        if not chunk:
            continue
        # If the chunk contains any Thai characters, it's considered a Thai chunk
        is_thai = contains_thai(chunk)
        result.append((chunk, is_thai))
        
    return result

def translate_mixed_text(text: str, translator) -> str:
    """
    Translates non-Thai parts of the text into Thai while leaving Thai parts intact.
    """
    if not text:
        return text
        
    chunks = split_thai_and_non_thai(text)
    translated_parts = []
    
    for chunk, is_thai in chunks:
        if is_thai:
            translated_parts.append(chunk)
        else:
            # Check if there are translatable characters (e.g. alphabetic letters)
            if any(char.isalpha() for char in chunk):
                try:
                    # Match leading whitespace, actual content, and trailing whitespace
                    match = re.match(r'^(\s*)(.*?)(\s*)$', chunk, re.DOTALL)
                    if match:
                        leading, content, trailing = match.groups()
                        if any(c.isalpha() for c in content):
                            # Translate the core content
                            translated = translator.translate(content)
                            translated_parts.append(f"{leading}{translated}{trailing}")
                        else:
                            translated_parts.append(chunk)
                    else:
                        translated = translator.translate(chunk)
                        translated_parts.append(translated)
                except Exception as e:
                    logger.error(f"Failed to translate chunk '{chunk}': {e}")
                    translated_parts.append(chunk)
            else:
                # Pure whitespace, punctuation, or numbers without letters
                translated_parts.append(chunk)
                
    return "".join(translated_parts)
