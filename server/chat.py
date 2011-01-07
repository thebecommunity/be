#!/usr/bin/env python

import deployment
import template
import auth
import db
import profile

import time
import cgi

def handle_report(environ, start_response):
    """Handles reporting of a chat message from a user."""

    if not auth.check_auth(environ, start_response):
        return []

    user_id = auth.user(environ)

    form = cgi.FieldStorage(fp=environ['wsgi.input'],
                            environ=environ)
    if 'msg' in form:
        msg = form['msg'].value
    else:
        msg = ''

    c = db.conn.cursor()
    vals = {
        'id' : user_id,
        'time' : int(time.time()),
        'msg' : msg
        }
    c.execute('insert into chat (user_id, time, msg) values(:id, :time, :msg)', vals)
    db.conn.commit()

    c.close()

    start_response('200 OK', [('Content-Type', 'text/html')])
    return []


class Message:
    def __init__(self, user, t, message):
        self.user = user
        self.time = t
        self.message = message

@template.output('chat_log.html')
def handle_log(environ, start_response):
    """Handles queries for the chat log."""

    if not auth.check_admin(environ, start_response):
        return []

    start_response('200 OK', [('Content-Type', 'text/html')])

    c = db.conn.cursor()
    # FIXME query string to control this, at a minimum limit the time span
    c.execute('select user_id,time,msg from chat')

    msgs = []
    for row in c:
        msg = Message(
            user=profile.name(row[0]),
            t=time.gmtime(int(row[1])),
            message=row[2]
            )
        msgs.append(msg)

    c.close()

    result = template.render(msgs=msgs)
    return [result]
