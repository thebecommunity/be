#!/usr/bin/env python

import db
import auth
import json

def lookup_profile(name):
    """Look up a user profile. Returns it as a set of key-value pairs."""
    c = db.conn.cursor()
    c.execute( 'select name,age from profiles where user_id = :id', { 'id' : name } )

    # Login should be unique
    results = c.fetchall()
    if len(results) != 1:
        print "Error:", len(results), "should be exactly one profile result. User", name
        c.close()
        return None
    (result,) = results

    c.close()

    return {
        'name' : result[0],
        'age' : result[1],
        'avatar' : {
            'url' : "static/femaleWalkIdleSit.dae",
            'scale' : 1.0
            }
        }

def name(user_id):
    """Look up a user's name by their user id."""
    c = db.conn.cursor()
    c.execute( 'select name from profiles where user_id = :id', { 'id' : user_id } )

    # Login should be unique
    results = c.fetchall()
    if len(results) != 1:
        c.close()
        return None
    (result,) = results

    c.close()

    return results[0]

def _extract_url_username(environ):
    # Extract the name from the url, e.g. /user/xyz/abc
    user = environ['PATH_INFO']
    user = user.replace('/', '', 1)
    user = user.replace('/profile/json', '', 1)

    return user

def handle_profile_json(environ, start_response):
    if not auth.check_auth(environ, start_response):
        return []

    user = _extract_url_username(environ)

    user_id = auth.lookup_userid(user)
    profile_info = lookup_profile(user_id)

    if profile_info == None:
        start_response('404 Not Found', [('Content-Type', 'application/json')])
        return []

    start_response('200 OK', [('Content-Type', 'application/json')])
    return [ json.dumps(profile_info) ]


def handle_profile_settings_js(environ, start_response):
    if not auth.check_auth(environ, start_response):
        return []

    user_id = auth.user(environ)
    profile_info = lookup_profile(user_id)

    if profile_info == None:
        start_response('404 Not Found', [('Content-Type', 'text/javascript')])
        return []

    start_response('200 OK', [('Content-Type', 'text/javascript')])
    return [ "UserSettings = ", json.dumps(profile_info) ]
