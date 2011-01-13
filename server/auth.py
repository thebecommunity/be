#!/usr/bin/env python

import deployment

"""Repoze.who stuff"""
from repoze.who.interfaces import IIdentifier
from repoze.who.interfaces import IChallenger
from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin
from repoze.who.plugins.cookie import InsecureCookiePlugin
from repoze.who.plugins.form import RedirectingFormPlugin
from repoze.who.plugins.sql import SQLAuthenticatorPlugin
from repoze.who.middleware import PluggableAuthenticationMiddleware
from repoze.who.classifiers import default_request_classifier

try:
    from hashlib import sha1
except ImportError: # Python < 2.5 #pragma NO COVERAGE
    from sha import new as sha1    #pragma NO COVERAGE

import urllib
import db
import template
import cgi
import profile

def hash_user_credential(cleartext_password):
    digest = sha1(cleartext_password).hexdigest()
    return digest

def validate_user_credential(cleartext_password, stored_password_hash):
    """Validates that the provided and hashed passwords match."""
    digest = hash_user_credential(cleartext_password)
    return (stored_password_hash == digest)

def request_auth(environ):
    """Adds a flag that triggers an auth request without requiring a 401 response."""
    environ['be.auth.challenge'] = True

def _challenge_decider(environ, status, headers):
    if status.startswith('401 ') or 'be.auth.challenge' in environ:
        return True
    return False

def create_auth_middleware(app):
    sqlpasswd = SQLAuthenticatorPlugin(
        'SELECT user_id, password FROM users WHERE login = :login',
        db.create_db_conn,
        validate_user_credential
        )
    auth_tkt = AuthTktCookiePlugin(deployment.cookie_secret, 'auth_tkt')
    form = RedirectingFormPlugin('/account/login', '/account/dologin', '/account/logout', 'auth_tkt')

    identifiers = [('form', form),('auth_tkt',auth_tkt)]
    authenticators = [('sql', sqlpasswd)]
    challengers = [('form',form)]
    mdproviders = []

    middleware = PluggableAuthenticationMiddleware(
        app,
        identifiers,
        authenticators,
        challengers,
        mdproviders,
        default_request_classifier,
        _challenge_decider
        )

    return middleware

def authorized(environ):
    """Checks if the user is logged in."""
    return ('repoze.who.identity' in environ)

def user(environ):
    """Returns the user identity for the current user."""
    return environ['repoze.who.identity']['repoze.who.userid']

def _handle_auth_failure(environ, start_response, redirect):
    if redirect:
        start_response('303 See Other', [('Content-Type', 'text/plain'), ('Location', redirect)])
    else:
        request_auth(environ)
        start_response('401 Unauthorized', [('Content-Type', 'text/plain')])

def check_auth(environ, start_response, redirect=None):
    """Checks if the user is logged in. Redirects them to the
    specified page and returns false if not authorized. Returns True
    if authorized."""

    if not authorized(environ):
        _handle_auth_failure(environ, start_response, redirect)
        return False

    return True

def lookup_userid(name):
    """Look up a user id based on the username."""
    c = db.conn.cursor()
    c.execute( 'select user_id from users where login = :login', { 'login' : name } )

    # Login should be unique
    results = c.fetchall()
    if len(results) != 1:
        c.close()
        return None
    (result,) = results
    result = result[0]

    c.close()

    return result

def username(user_id):
    """Look up a username based on the user id."""
    c = db.conn.cursor()
    c.execute( 'select login from users where user_id = :id', { 'id' : user_id } )

    # Login should be unique
    results = c.fetchall()
    if len(results) != 1:
        c.close()
        return None
    (result,) = results
    result = result[0]

    c.close()

    return result

def is_admin(user_id):
    """Look up if a user id has admin privileges."""
    c = db.conn.cursor()
    c.execute( 'select admin from users where user_id = :id', { 'id' : user_id } )

    # Login should be unique
    results = c.fetchall()
    if len(results) != 1:
        c.close()
        return None
    (result,) = results
    result = result[0]

    c.close()

    return (result != 0)

def check_admin(environ, start_response, redirect=None):
    """Checks if the user is logged in and an admin. Redirects them to the
    specified page and returns false if not authorized. Returns True
    if authorized."""

    if not check_auth(environ, start_response, redirect):
        return False

    user_id = user(environ)
    if not is_admin(user_id):
        _handle_auth_failure(environ, start_response, redirect)
        return False

    return True

@template.output('login.html')
def handle_login(environ, start_response):
    # If we're already authorized, put us back at the landing page
    if authorized(environ):
        start_response('303 See Other', [('Content-Type', 'text/plain'), ('Location', deployment.LandingPage)])
        return []

    # Otherwise, generate the form
    came_from = deployment.LandingPage
    if environ['QUERY_STRING'].startswith('came_from='):
        came_from = environ['QUERY_STRING'].replace('came_from=', '', 1)
        came_from = urllib.unquote(came_from)

    start_response('200 OK', [('Content-Type', 'text/html')])
    result = template.render(deployment=deployment, came_from=came_from)
    return [result]

def handle_logout(environ, start_response):
    request_auth(environ)
    # With no other obvious course of action, just redirect to the
    # dashboard, which will trigger the normal login procedure again
    start_response('303 See Other', [('Content-Type', 'text/plain'), ('Location', deployment.LandingPage)])
    return []

@template.output('passwd.html')
def handle_passwd(environ, start_response):
    # If we're already authorized, ignore
    if not check_auth(environ, start_response, redirect=deployment.LandingPage):
        return []

    if environ['REQUEST_METHOD'] == 'POST':
        form = cgi.FieldStorage(fp=environ['wsgi.input'],
                                environ=environ)
        if 'password' in form:
            user_id = user(environ)

            new_passwd = form['password'].value
            digest = hash_user_credential(new_passwd)

            c = db.conn.cursor()
            vals = {
                'id' : user_id,
                'password' : digest
                }
            c.execute('update users set password = :password where user_id = :id', vals)
            db.conn.commit()
            c.close()

            start_response('200 OK', [('Content-Type', 'text/html')])
            return []

    # If we got here, we didn't get a full change password post, so generate the form for it
    start_response('200 OK', [('Content-Type', 'text/html')])
    result = template.render(deployment=deployment)
    return [result]

from random import choice
import string

def GenPasswd(length=8, chars=string.letters + string.digits):
    return ''.join([choice(chars) for i in range(length)])

@template.output('adduser.html')
def handle_add(environ, start_response):
    # If we're already authorized, ignore
    if not check_admin(environ, start_response):
        return []

    new_username = ''
    new_passwd = ''
    if environ['REQUEST_METHOD'] == 'POST':
        form = cgi.FieldStorage(fp=environ['wsgi.input'],
                                environ=environ)
        if 'username' in form:
            new_username = form['username'].value
            new_passwd = GenPasswd()
            digest = hash_user_credential(new_passwd)

            c = db.conn.cursor()
            vals = {
                'login' : new_username,
                'password' : digest
                }
            c.execute('insert into users(login, password, admin) values(:login, :password, 0)', vals)
            db.conn.commit()
            c.close()

            # Extract the new user id and setup a blank profile
            new_userid = lookup_userid(new_username)
            profile.create_blank(new_userid, new_username)

    start_response('200 OK', [('Content-Type', 'text/html')])
    result = template.render(deployment=deployment, username=new_username, password=new_passwd)
    return [result]


def get_users_with_admin(admin_is=True):
    if admin_is:
        admin_val = 1
    else:
        admin_val = 0

    c = db.conn.cursor()
    c.execute('select login from users where admin = %d' % (admin_val))

    results = c.fetchall()
    results = [r[0] for r in results]

    c.close()
    return results

@template.output('set_admin.html')
def handle_set_admin(environ, start_response):
    # If we're already authorized, ignore
    if not check_admin(environ, start_response):
        return []

    if environ['REQUEST_METHOD'] == 'POST':
        form = cgi.FieldStorage(fp=environ['wsgi.input'],
                                environ=environ)
        if 'username' in form:
            username = form['username'].value

            c = db.conn.cursor()
            vals = {
                'username' : username
                }
            c.execute('update users set admin = 1 where login = :username', vals)
            db.conn.commit()
            c.close()

    # Get lists for both admins and non-admins
    admins = get_users_with_admin(True)
    not_admins = get_users_with_admin(False)

    start_response('200 OK', [('Content-Type', 'text/html')])
    result = template.render(deployment=deployment, admins=admins, not_admins=not_admins)
    return [result]
