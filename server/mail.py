#!/usr/bin/env

import smtplib
import deployment

def send(to, to_name, subject, body):
    server = deployment.Email['server']
    name = deployment.title
    user = deployment.Email['user']
    pwd = deployment.Email['password']

    smtpserver = smtplib.SMTP(server, 587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo()
    smtpserver.login(user, pwd)
    message = """From: %s <%s>
To: %s <%s>
Subject: %s

%s
""" % (name, user, to_name, to, subject, body)

    smtpserver.sendmail(user, to, message)
    smtpserver.close()
