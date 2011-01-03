#!/usr/bin/env python

import auth

def myapp(environ, start_response):
    if not auth.check_auth(environ, start_response):
        return []

    start_response('200 OK', [('Content-Type', 'text/plain')])
    return ['Hello World!\n']

if __name__ == '__main__':
    from flup.server.fcgi import WSGIServer

    app = auth.create_auth_middleware(myapp);
    WSGIServer(app, bindAddress=("localhost", 9999)).run()
