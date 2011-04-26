#!/usr/bin/python

import urllib
import sys


SHORTENNER_SERVER = "http://localhost:8080/url=%s"

def usage():
    print "%s <long url>" % sys.argv[0]

if len(sys.argv) != 2:
    print "Error: not enough args"
    usage()
else:
    long_url = sys.argv[1]
    fp = urllib.urlopen(SHORTENNER_SERVER % long_url)
    print fp.read()
    fp.close()
