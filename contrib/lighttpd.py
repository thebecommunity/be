#!/usr/bin/env python

# A simple wrapper for running lighttpd on your katajs.git
# directory. Generates an appropriate configuration and runs lighttpd
# with it.

import sys
import os
import tempfile

def main():

    port = 8888
    gzip_setting = ""
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    if len(sys.argv) > 2:
        gzip_setting = """compress.cache-dir         = "%s"
compress.filetype          = ("text/plain","text/css", "text/xml", "text/javascript")
""" % ( sys.argv[2] )

    conf = """
server.modules              = (
            "mod_access",
            "mod_alias",
            "mod_accesslog",
            "mod_compress",
            "mod_dirlisting",
            "mod_fastcgi"
)
server.document-root       = "%(pwd)s/"
server.errorlog            = "%(pwd)s/lighttpd.error.log"
index-file.names           = ( )
dir-listing.activate       = "enable"
accesslog.filename         = "%(pwd)s/lighttpd.access.log"
url.access-deny            = ( "~", ".inc" )
server.port               = %(port)d
%(gzip)s
#include_shell "/usr/share/lighttpd/create-mime.assign.pl"
# Set up the appropriate MIME type mappings
mimetype.assign             = (
  ".pdf"          =>      "application/pdf",
  ".sig"          =>      "application/pgp-signature",
  ".spl"          =>      "application/futuresplash",
  ".class"        =>      "application/octet-stream",
  ".ps"           =>      "application/postscript",
  ".torrent"      =>      "application/x-bittorrent",
  ".dvi"          =>      "application/x-dvi",
  ".gz"           =>      "application/x-gzip",
  ".pac"          =>      "application/x-ns-proxy-autoconfig",
  ".swf"          =>      "application/x-shockwave-flash",
  ".tar.gz"       =>      "application/x-tgz",
  ".tgz"          =>      "application/x-tgz",
  ".tar"          =>      "application/x-tar",
  ".zip"          =>      "application/zip",
  ".mp3"          =>      "audio/mpeg",
  ".m3u"          =>      "audio/x-mpegurl",
  ".wma"          =>      "audio/x-ms-wma",
  ".wax"          =>      "audio/x-ms-wax",
  ".ogg"          =>      "application/ogg",
  ".wav"          =>      "audio/x-wav",
  ".gif"          =>      "image/gif",
  ".jpg"          =>      "image/jpeg",
  ".jpeg"         =>      "image/jpeg",
  ".png"          =>      "image/png",
  ".xbm"          =>      "image/x-xbitmap",
  ".xpm"          =>      "image/x-xpixmap",
  ".xwd"          =>      "image/x-xwindowdump",
  ".css"          =>      "text/css",
  ".html"         =>      "text/html",
  ".htm"          =>      "text/html",
  ".js"           =>      "text/javascript",
  ".asc"          =>      "text/plain",
  ".c"            =>      "text/plain",
  ".cpp"          =>      "text/plain",
  ".log"          =>      "text/plain",
  ".conf"         =>      "text/plain",
  ".text"         =>      "text/plain",
  ".txt"          =>      "text/plain",
  ".dtd"          =>      "text/xml",
  ".xml"          =>      "text/xml",
  ".dae"          =>      "text/xml",
  ".mpeg"         =>      "video/mpeg",
  ".mpg"          =>      "video/mpeg",
  ".mov"          =>      "video/quicktime",
  ".qt"           =>      "video/quicktime",
  ".avi"          =>      "video/x-msvideo",
  ".asf"          =>      "video/x-ms-asf",
  ".asx"          =>      "video/x-ms-asf",
  ".wmv"          =>      "video/x-ms-wmv",
  ".bz2"          =>      "application/x-bzip",
  ".tbz"          =>      "application/x-bzip-compressed-tar",
  ".tar.bz2"      =>      "application/x-bzip-compressed-tar"
 )

server.error-handler-404 = "/404"

# Anything except the few static resources are handled by fcgi/our python scripts
$HTTP["url"] !~ "^/static/|^/css/|^/scripts/|^/externals/" {
    fastcgi.server = ("/" => ((
        "host" => "127.0.0.1",
        "port" => 9999,
        "check-local" => "disable",
        "disable-time" => 1,
        "fix-root-scriptname" => "enable"
    )))
}

#include_shell "/usr/share/lighttpd/include-conf-enabled.pl"
""" % { 'pwd' : os.getcwd(), 'port' : port, 'gzip' : gzip_setting }
    print conf

    tmp_conf_file = file('lighttpd.cfg', 'w') #tempfile.NamedTemporaryFile(delete = False)
    tmp_conf_file.write(conf)
    tmp_conf_file.close()

    print tmp_conf_file.name
    print 'lighttpd-angel -D -f %s' % (tmp_conf_file.name)
    os.system('lighttpd-angel -D -f %s' % (tmp_conf_file.name))
    return 0

if __name__ == "__main__":
    sys.exit(main())
