#!/usr/bin/env python

import db
import space
import template
import auth
import deployment
import cgi

def listing():
    # Gets a listing of all groups, sorted

    c = db.conn.cursor()
    c.execute( 'select group_id, name from groups order by group_id')

    # Login should be unique
    results = [ {'id' : x[0], 'name' : x[1]} for x in c.fetchall() ]
    return results


@template.output('groups.html')
def handle_admin(environ, start_response):
    if not auth.check_admin(environ, start_response):
        return []

    if environ['REQUEST_METHOD'] == 'POST':
        form = cgi.FieldStorage(fp=environ['wsgi.input'],
                                environ=environ)
        if 'name' in form:
            new_groupname = form['name'].value

            c = db.conn.cursor()
            vals = { 'name' : new_groupname }
            c.execute('insert into groups(name) values(:name)', vals)
            db.conn.commit()
            c.close()

    groups = listing()

    start_response('200 OK', [('Content-Type', 'text/html')])
    result = template.render(deployment=deployment, groups=groups)
    return [result]
