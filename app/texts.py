# Texts and data for the bot

QUOTES = [
    "Quote 1",
    "Quote 2",
    "Quote 3",
]

HELP_TEXT = "This is a help message"

def build_authors_keyboard():
    """Build inline keyboard for authors"""
    return []

def build_quote_text(full_name, quote):
    """Build quote text message"""
    return f"{full_name}\n{quote}"
