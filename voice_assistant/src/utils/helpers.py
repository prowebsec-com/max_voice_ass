import re

def clean_for_tts(text):
    """
    Removes emojis and special characters that shouldn't be spoken.
    """
    # Remove emojis (range of emojis)
    # This is a basic regex for common emojis
    # Allow alphanumeric, spaces, and punctuation: , ? . ! ' : -
    text = re.sub(r'[^\w\s,?.!\':-]', '', text)
    return text.strip()
