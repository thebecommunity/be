#!/usr/bin/env python

import deployment
import template
import auth
import db
import profile

import time
import cgi
import sanitize

def _extract_session_id(environ):
    form = cgi.FieldStorage(fp=environ['wsgi.input'],
                            environ=environ)

    # There should be a field for session id
    if 'sessid' not in form: return None
    sessid = form['sessid'].value
    if len(sessid) != 8: return None
    return sessid

def handle_begin(environ, start_response):
    """Starts a session."""

    if not auth.check_auth(environ, start_response):
        return []

    user_id = auth.user(environ)

    sessid = _extract_session_id(environ)
    if not sessid:
        start_response('200 OK', [('Content-Type', 'text/html')])
        return []

    c = db.conn.cursor()
    vals = {
        'id' : user_id,
        'sessid' : sessid,
        'time' : int(time.time()),
        }
    c.execute('insert into sessions (user_id, sess_id, start, end) values(:id, :sessid, :time, :time)', vals)
    db.conn.commit()

    c.close()

    start_response('200 OK', [('Content-Type', 'text/html')])
    return []


def handle_heartbeat(environ, start_response):
    """Heartbeat on a session, updates its ending time."""

    if not auth.check_auth(environ, start_response):
        return []

    user_id = auth.user(environ)

    sessid = _extract_session_id(environ)
    if not sessid:
        start_response('200 OK', [('Content-Type', 'text/html')])
        return []

    c = db.conn.cursor()
    vals = {
        'id' : user_id,
        'sessid' : sessid,
        'time' : int(time.time()),
        }
    c.execute('update sessions set end = :time where user_id = :id and sess_id = :sessid', vals)
    db.conn.commit()

    c.close()

    start_response('200 OK', [('Content-Type', 'text/html')])
    return []
