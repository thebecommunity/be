#!/usr/bin/env python
# Runs the space server and generates a pidfile for it

import subprocess
import sys

# We assume you did something of the form ./space_daemon.py /path/to/pidfile /path/to/space and some args
pidfile_name = sys.argv[1]
cmd_args = sys.argv[2:]
proc = subprocess.Popen(cmd_args)

pidfile = open(pidfile_name, 'w')
pidfile.write( str(proc.pid) )
pidfile.close()
