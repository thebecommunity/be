# This is a modified version of the sql plugin for
# repoze.who. Original copyright:
#
# Copyright: Copyright 2007 Agendaless Consulting and Contributors
# License:
#   A copyright notice accompanies this license document that identifies
#   the copyright holders.
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are
#   met:
#
#   1.  Redistributions in source code must retain the accompanying
#       copyright notice, this list of conditions, and the following
#       disclaimer.
#
#   2.  Redistributions in binary form must reproduce the accompanying
#       copyright notice, this list of conditions, and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#
#   3.  Names of the copyright holders must not be used to endorse or
#       promote products derived from this software without prior
#       written permission from the copyright holders.
#
#   4.  If any files are modified, you must cause the modified files to
#       carry prominent notices stating that you changed the files and
#       the date of any change.
#
#   Disclaimer
#
#     THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND
#     ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
#     TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
#     PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#     HOLDERS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#     EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
#     TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#     DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#     ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
#     TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
#     THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#     SUCH DAMAGE.


from zope.interface import implements

from repoze.who.interfaces import IAuthenticator
from repoze.who.interfaces import IMetadataProvider

def default_password_compare(cleartext_password, stored_password_hash):
    try:
        from hashlib import sha1
    except ImportError: # Python < 2.5 #pragma NO COVERAGE
        from sha import new as sha1    #pragma NO COVERAGE

    # the stored password is stored as '{SHA}<SHA hexdigest>'.
    # or as a cleartext password (no {SHA} prefix)

    if stored_password_hash.startswith('{SHA}'):
        stored_password_hash = stored_password_hash[5:]
        digest = sha1(cleartext_password).hexdigest()
    else:
        digest = cleartext_password

    if stored_password_hash == digest:
        return True

    return False

def make_psycopg_conn_factory(**kw):
    # convenience (I always seem to use Postgres)
    def conn_factory(): #pragma NO COVERAGE
        import psycopg2 #pragma NO COVERAGE
        return psycopg2.connect(kw['repoze.who.dsn']) #pragma NO COVERAGE
    return conn_factory #pragma NO COVERAGE

class SQLAuthenticatorPlugin:
    implements(IAuthenticator)

    def __init__(self, query, conn_factory, hash_fn, compare_fn):
        # statement should be pyformat dbapi binding-style, e.g.
        # "select user_id, password from users where login=%(login)s"
        self.query = query
        self.conn_factory = conn_factory
        self.hash_fn = hash_fn
        self.compare_fn = compare_fn or default_password_compare
        self.conn = None

    # IAuthenticator
    def authenticate(self, environ, identity):
        if not 'login' in identity or not 'password' in identity:
            return None
        identity['login'] = unicode(identity['login'], 'utf-8')
        identity['hashed_password'] = self.hash_fn(identity['password'])
        if not self.conn:
            self.conn = self.conn_factory()
        curs = self.conn.cursor()
        curs.execute(self.query, identity)
        result = curs.fetchone()
        curs.close()
        if result:
            user_id, password = result
            if self.compare_fn(identity['password'], password):
                return user_id

class SQLMetadataProviderPlugin:
    implements(IMetadataProvider)

    def __init__(self, name, query, conn_factory, filter):
        self.name = name
        self.query = query
        self.conn_factory = conn_factory
        self.filter = filter
        self.conn = None

    # IMetadataProvider
    def add_metadata(self, environ, identity):
        if self.conn is None:
            self.conn = self.conn_factory()
        curs = self.conn.cursor()
        # can't use dots in names in python string formatting :-(
        identity['__userid'] = identity['repoze.who.userid']
        curs.execute(self.query, identity)
        result = curs.fetchall()
        if self.filter:
            result = self.filter(result)
        curs.close()
        del identity['__userid']
        identity[self.name] =  result

def make_authenticator_plugin(query=None, conn_factory=None,
                              compare_fn=None, **kw):
    from repoze.who.utils import resolveDotted
    if query is None:
        raise ValueError('query must be specified')
    if conn_factory is None:
        raise ValueError('conn_factory must be specified')
    try:
        conn_factory = resolveDotted(conn_factory)(**kw)
    except Exception, why:
        raise ValueError('conn_factory could not be resolved: %s' % why)
    if compare_fn is not None:
        compare_fn = resolveDotted(compare_fn)
    return SQLAuthenticatorPlugin(query, conn_factory, compare_fn)

def make_metadata_plugin(name=None, query=None, conn_factory=None,
                         filter=None, **kw):
    from repoze.who.utils import resolveDotted
    if name is None:
        raise ValueError('name must be specified')
    if query is None:
        raise ValueError('query must be specified')
    if conn_factory is None:
        raise ValueError('conn_factory must be specified')
    try:
        conn_factory = resolveDotted(conn_factory)(**kw)
    except Exception, why:
        raise ValueError('conn_factory could not be resolved: %s' % why)
    if filter is not None:
        filter = resolveDotted(filter)
    return SQLMetadataProviderPlugin(name, query, conn_factory, filter)
