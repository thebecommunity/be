#!/usr/bin/env python

import auth
import deployment
import template
import profile

@template.output('dashboard.html')
def handle_dashboard(environ, start_response):
    # Redirect to landing page if they aren't authorized
    if not auth.check_auth(environ, start_response):
        return []

    user_id = auth.user(environ)
    name = profile.name(user_id)
    admin = auth.is_admin(user_id)

    start_response('200 OK', [('Content-Type', 'text/html')])
    result = template.render(deployment=deployment, name=name, admin=admin)
    return [result]
