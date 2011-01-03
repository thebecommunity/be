#!/usr/bin/env python

"""Repoze.who stuff"""
from repoze.who.interfaces import IIdentifier
from repoze.who.interfaces import IChallenger
from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin
from repoze.who.plugins.cookie import InsecureCookiePlugin
from repoze.who.plugins.form import FormPlugin
from repoze.who.plugins.sql import SQLAuthenticatorPlugin
from repoze.who.middleware import PluggableAuthenticationMiddleware
from repoze.who.classifiers import default_request_classifier
from repoze.who.classifiers import default_challenge_decider

try:
    from hashlib import sha1
except ImportError: # Python < 2.5 #pragma NO COVERAGE
    from sha import new as sha1    #pragma NO COVERAGE

import sqlite3

def hash_user_credential(cleartext_password):
    digest = sha1(cleartext_password).hexdigest()
    return digest

def validate_user_credential(cleartext_password, stored_password_hash):
    """Validates that the provided and hashed passwords match."""
    digest = hash_user_credential(cleartext_password)
    return (stored_password_hash == digest)

def create_db_conn():
    return sqlite3.connect('be.db', check_same_thread = False)

def create_auth_middleware(app):
    sqlpasswd = SQLAuthenticatorPlugin(
        'SELECT user_id, password FROM users WHERE login = :login',
        create_db_conn,
        validate_user_credential
        )
    auth_tkt = AuthTktCookiePlugin('secret', 'auth_tkt')
    form = FormPlugin('__do_login', rememberer_name='auth_tkt')

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

def check_auth(environ, start_response):
    """Checks if the user is logged in. Generates 401 and returns
    False if not authorized. Returns True if authorized."""

    if not 'repoze.who.identity' in environ:
        start_response('401 Unauthorized', [('Content-Type', 'text/plain')])
        return False

    return True
