#!/usr/bin/env python

import deployment
import template
import auth

@template.output('viewer.html')
def handle_viewer(environ, start_response):
    if not auth.check_auth(environ, start_response):
        return []

    start_response('200 OK', [('Content-Type', 'text/html')])
    result = template.render(deployment=deployment)
    return [result]
