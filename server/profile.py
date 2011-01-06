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
        c.close()
        return None
    (result,) = results

    c.close()

    return {
        'name' : result[0],
        'age' : result[1]
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

def handle_profile_json(environ, start_response):
    if not auth.check_auth(environ, start_response):
        return []

    # Extract the name from the url. /user/profile/json
    user = environ['PATH_INFO']
    user = user.replace('/', '', 1)
    user = user.replace('/profile/json', '', 1)

    user_id = auth.lookup_userid(user)
    profile_info = lookup_profile(user_id)

    if profile_info == None:
        start_response('404 Not Found', [('Content-Type', 'application/json')])
        return []

    start_response('200 OK', [('Content-Type', 'application/json')])
    return [ json.dumps(profile_info) ]
