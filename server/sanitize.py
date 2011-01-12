#!/usr/bin/env python

from genshi.filters import HTMLSanitizer
from genshi.input import HTML

class TextSanitizer(HTMLSanitizer):
    """A filter that sanitizes all HTML from the input, leaving raw text."""
    def __init__(self):
        HTMLSanitizer.__init__(self, safe_tags=set(), safe_attrs=set(), safe_schemes=set(), uri_attrs=set())

def html(data):
    return str(HTML(data) | HTMLSanitizer())

def text(data):
    return str(HTML(data) | TextSanitizer())

def integer(data):
    return int(text(data))
