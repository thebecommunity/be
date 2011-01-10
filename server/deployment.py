#!/usr/bin/env python

# Deployment configuration. Customize for your deployment.

# Filename for SQLite database
db_filename = 'be.db'

# This *must* be changed or your login cookies will not be secure.
cookie_secret = 'secret'

# Deployment name
title = "the BE community"

# Replace to override the default of using the sirikata protocol on
# the same host on Sirikata's default port of 7777. Note that this is
# a javascript string
SpaceURL = '"sirikata://" + window.location.hostname + ":7777"'

Avatars = {
    "Male" :
    {
        'name' : "Male",
        'url' : "maleWalkIdleSit.dae",
        'scale' : 1.0,
        'preview' : "maleheadshot.png"
    },
    "Female" :
    {
        'name' : "Female",
        'url' : "femaleWalkIdleSit.dae",
        'scale' : 1.0,
        'preview' : "femaleheadshot.png"
    }
}
DefaultAvatar = "Male"
