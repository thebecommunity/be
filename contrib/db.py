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


conn = sqlite3.connect('be.db')


argi = 1
while argi < len(sys.argv):
    arg = sys.argv[argi]
    if arg == 'init':
        conn.execute('create table if not exists users (user_id integer primary key, login text unique, password text)')
        conn.execute('create table if not exists profiles (user_id integer primary key, name text, age integer)')
        conn.execute('create table if not exists chat (user_id integer, time integer, msg text)')
        argi += 1
    elif arg == 'adduser':
        name = sys.argv[argi+1]
        pw = hash_user_credential(sys.argv[argi+2])
        conn.execute('insert into users(login, password) values(?, ?)', (name, pw))
        argi += 3
    else:
        print "Ignoring unknown command:", arg
        argi += 1

conn.commit()
conn.close()
