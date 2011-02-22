#!/usr/bin/env python

import deployment

"""Repoze.who stuff"""
from repoze.who.interfaces import IIdentifier
from repoze.who.interfaces import IChallenger
from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin
from repoze.who.plugins.cookie import InsecureCookiePlugin
from repoze.who.plugins.form import RedirectingFormPlugin
from sqlauth import SQLAuthenticatorPlugin
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
import groups
import mail

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
        'SELECT user_id, password FROM users NATURAL JOIN profiles WHERE (login = :login or name = :login) and password = :hashed_password',
        db.create_db_conn,
        hash_user_credential,
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

    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
    result = template.render(deployment=deployment, came_from=came_from)
    return [result]

def handle_logout(environ, start_response):
    request_auth(environ)
    # With no other obvious course of action, just redirect to the
    # dashboard, which will trigger the normal login procedure again
    start_response('303 See Other', [('Content-Type', 'text/plain'), ('Location', deployment.LandingPage)])
    return []

def _set_passwd(user_id, new_passwd):
    digest = hash_user_credential(new_passwd)

    c = db.conn.cursor()
    vals = {
        'id' : user_id,
        'password' : digest
        }
    c.execute('update users set password = :password where user_id = :id', vals)
    db.conn.commit()
    c.close()

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

            _set_passwd(user_id, new_passwd)

            start_response('303 See Other', [('Content-Type', 'text/plain'), ('Location', deployment.LandingPage)])
            return []

    # If we got here, we didn't get a full change password post, so generate the form for it
    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
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

    # We must have groups setup
    all_groups = groups.listing()
    if not all_groups:
        start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
        result = template.render(deployment=deployment, username=new_username, password=new_passwd, need_group=True, existing_user=False)
        return [result]

    if environ['REQUEST_METHOD'] == 'POST':
        form = cgi.FieldStorage(fp=environ['wsgi.input'],
                                environ=environ)
        if 'username' in form and 'group' in form and 'email' in form:
            new_username = unicode(form['username'].value, 'utf-8')
            new_passwd = GenPasswd()
            digest = hash_user_credential(new_passwd)

            new_group_id = form['group'].value
            new_email = form['email'].value

            existing_userid = lookup_userid(new_username)
            if existing_userid != None:
                start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
                result = template.render(deployment=deployment, username='', password='', need_group=False, existing_user=True, groups=all_groups)
                return [result]

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
            profile.create_blank(new_userid, new_username, new_group_id, new_email)

            # Email the new user with the info
            mail.send(
                new_email, new_username,
                "Welcome to %s!" % (deployment.title),
                """Welcome!

Your new account, with username '%s' has been created.  Your temporary password is '%s'.  Please change it the next time you log in.

Thanks,
%s
""" % (new_username, new_passwd, deployment.title)
                )
    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
    result = template.render(deployment=deployment, username=new_username, password=new_passwd, need_group=False, existing_user=False, groups=all_groups)
    return [result]


@template.output('forgot_password.html')
def handle_forgot(environ, start_response):
    # Unlike usual, if we're authorized, this is not the right page for them.
    if authorized(environ):
        start_response('303 See Other', [('Content-Type', 'text/plain'), ('Location', deployment.LandingPage)])
        return []

    # If we have an email address, do the lookup & reset and generate a simple response page.
    reset_tried = False
    reset_succeeded = False
    email = ''
    if environ['REQUEST_METHOD'] == 'POST':
        form = cgi.FieldStorage(fp=environ['wsgi.input'],
                                environ=environ)
        if 'email' in form:
            email = form['email'].value
            reset_tried = True

            # Lookup this email address
            user_id = profile.userid_by_email(email)
            if user_id:
                new_passwd = GenPasswd()
                _set_passwd(user_id, new_passwd)

                profile_info = profile.lookup_profile(user_id)
                # Email the new user with the info
                mail.send(
                    email, profile_info['name'],
                    "Reset Password for %s!" % (deployment.title),
                    """A password reset was requested for the account '%s' associated with this email address.  Your new temporary password is '%s'. Please change it the next time you log in.

Thanks,
%s
""" % (profile_info['name'], new_passwd, deployment.title)
                    )

                reset_succeeded = True

    # Otherwise, generate the form
    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
    result = template.render(deployment=deployment, reset_tried=reset_tried, reset_succeeded=reset_succeeded, email=email)
    return [result]



def get_users():
    c = db.conn.cursor()
    c.execute('select login from users')

    results = c.fetchall()
    results = [r[0] for r in results]

    c.close()
    return results

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

def update_admin(username, admin_setting):
    c = db.conn.cursor()
    vals = {
        'username' : username,
        'admin' : admin_setting
        }
    c.execute('update users set admin = :admin where login = :username', vals)
    db.conn.commit()
    c.close()

def delete_user(username):
    userid = lookup_userid(username)

    # We need to sanity check that they aren't going to make the database break.
    c = db.conn.cursor()
    vals = {
        'id' : userid,
        }
    c.execute('select * from chat where user_id = :id', vals)
    results = c.fetchall()
    if len(results) > 0: return 'Cannot delete a user who appears in the chat log.'

    c.execute('select * from sessions where user_id = :id', vals)
    if len(results) > 0: return 'Cannot delete a user who appears in the session log.'

    c.execute('delete from users where user_id = :id', vals)
    c.execute('delete from profiles where user_id = :id', vals)

    db.conn.commit()
    c.close()

@template.output('account_admin.html')
def handle_account_admin(environ, start_response):
    # If we're already authorized, ignore
    if not check_admin(environ, start_response):
        return []

    msg = '' # Message for actions taken
    if environ['REQUEST_METHOD'] == 'POST':
        form = cgi.FieldStorage(fp=environ['wsgi.input'],
                                environ=environ)
        if 'username' in form and 'action' in form:
            username = unicode(form['username'].value, 'utf-8')
            action = form['action'].value

            if action == 'admin':
                update_admin(username, 1)
                msg = 'User admin status updated.'
            elif action == 'revoke':
                update_admin(username, 0)
                msg = 'User admin status updated.'
            elif action == 'delete':
                msg = delete_user(username)

    # Get lists for both admins and non-admins
    admins = get_users_with_admin(True)
    not_admins = get_users_with_admin(False)
    users = get_users()

    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
    result = template.render(deployment=deployment, users=users, admins=admins, not_admins=not_admins, msg=msg)
    return [result]
