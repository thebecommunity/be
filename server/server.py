#!/usr/bin/env python

import notfound
import auth
import profile
import viewer
import chat

import re

static_handlers = {
    "/404" : notfound.handle_404,
    "/account/login" : auth.handle_login,
    "/account/dologin" : auth.handle_login,
    "/account/logout" : auth.handle_logout,
    "/account/password" : auth.handle_passwd,
    "/account/add" : auth.handle_add,
    "/account/settings.js" : profile.handle_profile_settings_js,
    "/profile/edit" : profile.handle_edit,
    "/viewer" : viewer.handle_viewer,
    "/chat/report" : chat.handle_report,
    "/chat/log" : chat.handle_log
    }

dynamic_handlers = {
    re.compile('.*/profile/json') : profile.handle_profile_json,
    }

def myapp(environ, start_response):
    doc = environ['PATH_INFO']
    if doc in static_handlers:
        return static_handlers[doc](environ, start_response)

    for pat,handler in dynamic_handlers.items():
        mat = pat.match(doc)
        if mat: return handler(environ, start_response)

    start_response('404 Not Found', [('Content-Type', 'text/plain')])
    return []

if __name__ == '__main__':
    from flup.server.fcgi import WSGIServer

    app = auth.create_auth_middleware(myapp);
    WSGIServer(app, bindAddress=("localhost", 9999)).run()
