#!/usr/bin/env python

import sqlite3

def create_db_conn():
    return sqlite3.connect(deployment.db_filename, check_same_thread = False)
