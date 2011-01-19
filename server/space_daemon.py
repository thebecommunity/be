#!/usr/bin/env python
# Runs the space server and generates a pidfile for it

import subprocess
import sys

if sys.argv[1] == 'kill':
    pid_p = subprocess.Popen(['cat', sys.argv[2]], stdout=subprocess.PIPE)
    (pid, piderr) = pid_p.communicate()
    subprocess.call(['kill', str(pid)])
else:
    # We assume you did something of the form ./space_daemon.py /path/to/pidfile /path/to/space and some args
    pidfile_name = sys.argv[1]
    cmd_args = sys.argv[2:]
    proc = subprocess.Popen(cmd_args, stdout=sys.stdout, stderr=sys.stderr)

    pidfile = open(pidfile_name, 'w')
    pidfile.write( str(proc.pid) )
    pidfile.close()
