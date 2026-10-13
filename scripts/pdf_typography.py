"""Embed an available font for every character without changing source text."""
import re
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Paragraph as BaseParagraph


class Paragraph(BaseParagraph):
    def __init__(self, text, style=None, *args, **kwargs):
        if text and style:
            font = pdfmetrics.getFont(style.fontName)
            if hasattr(font.face, 'charWidths'):
                parts = re.split(r'(<[^>]*>)',text)
                for i in range(0,len(parts),2):
                    def fallback(match):
                        char = match[0]
                        if ord(char) in font.face.charWidths:return char
                        for name in ('Edition','Folio-Serif','Edition-Japanese'):
                            if name in pdfmetrics.getRegisteredFontNames() and ord(char) in pdfmetrics.getFont(name).face.charWidths:
                                return '<font name="'+name+'">'+char+'</font>'
                        raise ValueError(f'No printable glyph for {char!r} in {style.fontName}')
                    parts[i]=re.sub(r'[^\x00-\x7f]',fallback,parts[i])
                text=''.join(parts)
        super().__init__(text,style,*args,**kwargs)
