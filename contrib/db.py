#!/usr/bin/env python

import sys
import sqlite3

try:
    from hashlib import sha1
except ImportError: # Python < 2.5 #pragma NO COVERAGE
    from sha import new as sha1    #pragma NO COVERAGE

def hash_user_credential(cleartext_password):
    digest = sha1(cleartext_password).hexdigest()
    return digest


conn = sqlite3.connect('data/be.db')


argi = 1
while argi < len(sys.argv):
    arg = sys.argv[argi]
    if arg == 'init':
        conn.execute('create table if not exists users (user_id integer primary key, login text unique, password text, admin integer)')
        conn.execute('create table if not exists profiles (user_id integer primary key, email text, name text, age integer, avatar text, group_id integer)')

        conn.execute('create table if not exists groups (group_id integer primary key, name text unique)')

        conn.execute('create table if not exists chat (user_id integer, time integer, msg text)')

        conn.execute('create table if not exists session_auth (ticket text, time integer)')
        conn.execute('create table if not exists sessions (user_id integer, sess_id text, start integer, end integer)')
        argi += 1
    elif arg == 'admin':
        # Note that these users are always admins, i.e. this is only
        # for bootstrapping. Use the web interface for adding normal
        # users
        name = sys.argv[argi+1]
        pw = hash_user_credential(sys.argv[argi+2])
        conn.execute('insert into users(user_id, login, password, admin) values(0, ?, ?, 1)', (name, pw))
        conn.execute('insert into profiles(user_id,name,age,avatar) values(0, ?, ?, ?)', (name, 0, ''))
        argi += 3
    else:
        print "Ignoring unknown command:", arg
        argi += 1

conn.commit()
conn.close()
