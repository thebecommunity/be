#!/usr/bin/env python

def handle_404(environ, start_response):
    start_response('404 Not Found', [('Content-Type', 'text/plain')])
    return ["Not found."]
