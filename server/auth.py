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
from repoze.who.classifiers import default_challenge_decider

try:
    from hashlib import sha1
except ImportError: # Python < 2.5 #pragma NO COVERAGE
    from sha import new as sha1    #pragma NO COVERAGE

import urllib
import db

def hash_user_credential(cleartext_password):
    digest = sha1(cleartext_password).hexdigest()
    return digest

def validate_user_credential(cleartext_password, stored_password_hash):
    """Validates that the provided and hashed passwords match."""
    digest = hash_user_credential(cleartext_password)
    return (stored_password_hash == digest)

def create_auth_middleware(app):
    sqlpasswd = SQLAuthenticatorPlugin(
        'SELECT user_id, password FROM users WHERE login = :login',
        db.create_db_conn,
        validate_user_credential
        )
    auth_tkt = AuthTktCookiePlugin(deployment.cookie_secret, 'auth_tkt')
    form = RedirectingFormPlugin('/login', '/dologin', '/logout', 'auth_tkt')

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
        default_challenge_decider
        )

    return middleware

def authorized(environ):
    """Checks if the user is logged in."""
    return ('repoze.who.identity' in environ)

def check_auth(environ, start_response):
    """Checks if the user is logged in. Generates 401 and returns
    False if not authorized. Returns True if authorized."""

    if not authorized(environ):
        start_response('401 Unauthorized', [('Content-Type', 'text/plain')])
        return False

    return True


def handle_login(environ, start_response):
    # Always generate a normal page
    start_response('200 OK', [('Content-Type', 'text/html')])

    # If we're already authorized, ignore
    if authorized(environ):
        return []

    # Otherwise, generate the form
    came_from_field = ''
    if environ['QUERY_STRING'].startswith('came_from='):
        came_from = environ['QUERY_STRING'].replace('came_from=', '', 1)
        came_from = urllib.unquote(came_from)
        came_from_field = '<input type="hidden" name="came_from" value="%s"></input>' % (came_from)

    frm = """
<html>
<head>
  <title>Log In</title>
</head>
<body>
  <div>
     <b>Log In</b>
  </div>
  <br/>
  <form method="POST" action="/dologin">
    %s
    <table border="0">
    <tr>
      <td>User Name</td>
      <td><input type="text" name="login"></input></td>
    </tr>
    <tr>
      <td>Password</td>
      <td><input type="password" name="password"></input></td>
    </tr>
    <tr>
      <td></td>
      <td><input type="submit" name="submit" value="Log In"/></td>
    </tr>
    </table>
  </form>
</body>
</html>
""" % (came_from_field)
    return [frm]

def handle_logout(environ, start_response):
    # Returning 401 triggers the cookie removal
    start_response('401 Unauthorized', [('Content-Type', 'text/plain')])
    return []
