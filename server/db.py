#!/usr/bin/env python

import sqlite3
import deployment

def create_db_conn():
    return sqlite3.connect(deployment.db_filename, check_same_thread = False)

# Provide a connection for default use
conn = create_db_conn()
