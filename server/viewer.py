#!/usr/bin/env python

import deployment
import template
import auth
import random
import db
import time

@template.output('viewer.html')
def handle_viewer(environ, start_response):
    if not auth.check_auth(environ, start_response):
        return []

    # Generate a ticket for the user to login with
    space_auth = auth.GenPasswd()

    # Insert into db so the space server can verify it
    c = db.conn.cursor()
    vals = {
        'ticket' : space_auth,
        'time' : int(time.time()),
        }
    c.execute('insert into session_auth(ticket, time) values(:ticket, :time)', vals)
    c.close()
    db.conn.commit()

    start_response('200 OK', [('Content-Type', 'text/html')])
    result = template.render(deployment=deployment, auth=space_auth)
    return [result]
