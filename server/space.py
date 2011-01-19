#!/usr/bin/env python

import db
import subprocess
import os.path
import stat
import time

_ServerDir = os.path.dirname(__file__)
_TopDir = os.path.join(_ServerDir, '..')
_SirikataDir = os.path.join(_TopDir, '..', 'sirikata.git')

def _pidfile(name):
    return os.path.join(_TopDir, 'sirikata-space-server-%s.pid' % (name))

def _cfgfile():
    return os.path.join(_TopDir, 'sirikata-space-server.monitrc')

def _generate_config():
    name = 'x'

    cfg = """
    set daemon 15
    set logfile %(topdir)s/monit.log
    set httpd port 2812
      use address localhost
      allow localhost

    check process sirikata-space-server-%(name)s
      with pidfile "%(pid)s"
      start program = "%(serverdir)s/space_daemon.py %(pid)s %(sirikatadir)s/build/cmake/space --space.plugins=weight-exp,weight-sqr,weight-const,space-null,space-local,space-standard,colladamodels,space-sqlite --auth=sqlite --auth-options=--db=%(topdir)s/be.db" with timeout 60 seconds
      stop program = "/bin/kill `cat %(pid)s`"
      if 2 restarts within 3 cycles then timeout
      if totalmem > 400 Mb then alert
      if children > 255 for 5 cycles then stop
    """ % { 'name' : name, 'pid' : _pidfile(name), 'port' : 7777, 'topdir' : _TopDir, 'serverdir' : _ServerDir, 'sirikatadir' : _SirikataDir }

    f = open(_cfgfile(), 'w')
    f.write(cfg)
    f.close()

    os.chmod(_cfgfile(), stat.S_IRUSR | stat.S_IWUSR)


def update():
    """Updates an active monit session's config."""
    _generate_config()
    subprocess.call(['monit', '-c', _cfgfile(), 'reload'])

def run():
    # Kill an instance if it's already running
    subprocess.call(['monit', '-c', _cfgfile(), '-I', 'quit'])
    time.sleep(1)
    # Generate config and run
    _generate_config()
    subprocess.call(['monit', '-c', _cfgfile()])
    time.sleep(1)
    # Monit isn't enabling monitoring by default, so trigger it manually
    subprocess.call(['monit', '-c', _cfgfile(), 'start', 'all'])
