#!/usr/bin/env python

import auth
import deployment
import template
import profile

@template.output('dashboard.html')
def handle_dashboard(environ, start_response):
    # Redirect to landing page if they aren't authorized
    if not auth.authorized(environ):
        start_response('303 See Other', [('Content-Type', 'text/plain'), ('Location', deployment.LandingPage)])
        return []

    user_id = auth.user(environ)
    name = profile.name(user_id)
    admin = auth.is_admin(user_id)

    start_response('200 OK', [('Content-Type', 'text/html')])
    result = template.render(deployment=deployment, name=name, admin=admin)
    return [result]
