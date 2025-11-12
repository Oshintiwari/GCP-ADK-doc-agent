from pathlib import Path

def short_name(path: str) -> str:
    """
    Return a clean filename without directories or '+' signs.
    Example:
        "data\\Conversational+Receptiveness+-+Expressing+engagement+with+opposing+views..pdf"
        → "Conversational Receptiveness - Expressing engagement with opposing views..pdf"
    """
    name = Path(path).name.replace('+', ' ')
    return name
