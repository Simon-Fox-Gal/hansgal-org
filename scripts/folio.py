"""Presentation-only helpers for work pages; catalogue data stays untouched."""
import html
import re


def present(value):
    text = html.unescape(re.sub(r'<[^>]*>', '', str(value or ''))).strip()
    return bool(text and text != '0') or bool(re.search(r'<(?:img|audio|iframe)\b', str(value or ''), re.I))


def folio_duration(value):
    text = str(value or '').strip()
    if not present(text):
        return ''
    return text + '′' if re.fullmatch(r'\d+(?:[.,]\d+)?', text) else text


def folio_title(title, original):
    """Give an explicitly recorded translation its own typographic line."""
    if original and title.startswith(original):
        suffix=title[len(original):]
        if suffix.strip().startswith(('(', '[', '［')):
            return original+'<span class="folio-translation">'+suffix+'</span>'
    return title
