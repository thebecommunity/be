#!/usr/bin/env python

import db
import space
import template
import auth
import deployment
import cgi
import space

port_base = 7900

def port(group_id):
    """Gets the port that a specific group's space server will be located on."""
    return port_base + int(group_id)


def listing():
    # Gets a listing of all groups, sorted by id

    c = db.conn.cursor()
    c.execute( 'select group_id, name from groups order by group_id')

    results = [ {'id' : x[0], 'name' : x[1], 'port' : port(x[0])} for x in c.fetchall() ]
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

            # If we were successful, we need another space server
            space.update()

    groups = listing()

    start_response('200 OK', [('Content-Type', 'text/html')])
    result = template.render(deployment=deployment, groups=groups)
    return [result]
