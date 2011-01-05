#!/usr/bin/env python

import notfound
import auth

static_handlers = {
    "/404" : notfound.handle_404,
    "/login" : auth.handle_login,
    "/dologin" : auth.handle_login,
    "/logout" : auth.handle_logout,
    }

def myapp(environ, start_response):
    if environ['PATH_INFO'] in static_handlers:
        return static_handlers[ environ['PATH_INFO'] ](environ, start_response)

    if not auth.check_auth(environ, start_response):
        return []

    start_response('200 OK', [('Content-Type', 'text/plain')])
    return ['Hello World!\n']

if __name__ == '__main__':
    from flup.server.fcgi import WSGIServer

    app = auth.create_auth_middleware(myapp);
    WSGIServer(app, bindAddress=("localhost", 9999)).run()
