#!/usr/bin/env python

# Deployment configuration. Customize for your deployment.

# Filename for SQLite database
db_filename = 'data/be.db'

# This *must* be changed or your login cookies will not be secure.
cookie_secret = 'secret'

# To send emails, we need some information about the
Email = {
    'server' : 'smtp.example.com',
    'user' : 'user@example.com',
    'password' : 'password'
    }

# Deployment name
title = "the BE community"

# Page to use as landing page, and redirect to when they aren't logged
# in. Defaults to the login page provided by the app, but could also
# be directed at another site that has a compatible login form
LandingPage = "/"
LoginPage = "/account/login"

# Replace to override the default of using the sirikata protocol on
# the same host.
SpaceURL = '"sirikata://" + window.location.hostname'

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
    },
    "MaleBrown" :
    {
        'name' : "MaleBrown",
        'url' : "maleWalkIdleSitBrown.dae",
        'scale' : 1.0,
        'preview' : "malebrownheadshot.png"
    },
    "FemaleBlonde" :
    {
        'name' : "FemaleBlonde",
        'url' : "femaleWalkIdleSitBlonde.dae",
        'scale' : 1.0,
        'preview' : "femaleblondeheadshot.png"
    }
}
DefaultAvatar = "Male"

HelpLink = "http://github.com/sirikata/kataspace/issues"
HelpText = "Report An Issue"
