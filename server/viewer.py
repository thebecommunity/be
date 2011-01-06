#!/usr/bin/env python

import deployment
import template

@template.output('viewer.html')
def handle_viewer(environ, start_response):
    # Always generate a normal page
    start_response('200 OK', [('Content-Type', 'text/html')])

    # If we're already authorized, ignore
    #if authorized(environ):
    #    return []

    result = template.render()
    return [result]
