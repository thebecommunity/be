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


class Session:
    def __init__(self, start, end):
        self.start = start
        self.end = end

class UserSessions:
    def __init__(self, user):
        self.user = user
        self.sessions = []

    def add(self, start, end):
        self.sessions.append( Session(start, end) )

@template.output('session_log.html')
def handle_log(environ, start_response):

    if not auth.check_admin(environ, start_response):
        return []

    start_response('200 OK', [('Content-Type', 'text/html')])

    c = db.conn.cursor()
    # FIXME query string to control this, at a minimum limit the time span
    c.execute('select user_id,start,end from sessions order by user_id,start')

    sessions = []
    last_user_id = None
    last_user = None

    for row in c:
        user_id = row[0]
        if user_id != last_user_id:
            last_user_id = user_id
            last_user = UserSessions(profile.name(user_id))
            sessions.append(last_user)
        last_user.add(
            time.gmtime(int(row[1])),
            time.gmtime(int(row[2]))
            )

    c.close()

    result = template.render(deployment=deployment,users=sessions)
    return [result]
