#!/usr/bin/env python

# Christian Wirtz <doc@snowheaven.de>
# Github: @doctore74
#
# checkmk datasource program for Telekom Speedport hybrid 
# Firmware-Version 050124.04.00.005
#
# Output will be printed in <<<local>>> section.

#######################################################################
#  Copyright (C) 2019 Christian Wirtz <doc@snowheaven.de>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#######################################################################

# checkmk
# https://mathias-kettner.com/
# Successfully tested on checkmk RAW version 1.6.0 (stable)
# 
# Path:
# Place this into /omd/sites/<SITE>/local/bin/
# Make this script executable!
#
# Configure:
# WATO -> Datasource Programs -> Individual program call instead of agent access -> Command line to execute
# check_speedport_hybrid.py --host $HOSTADDRESS$
#
# Local network http links without authentication
# HTML: http://<speedport-address>/html/login/status.html?lang=en
# JSON: http://<speedport-address>/data/Status.json
#
# Changelog

###########################
version      = "1.0"
version_date = "2019-11-21"
###########################


import sys
import getopt
import json
import urllib
from pprint import pprint
try:
    # For Python 3.0 and above
    from urllib.request import urlopen
except ImportError:
    # default: Python 2
    from urllib2 import urlopen


def print_version():
    print "Christian Wirtz <doc@snowheaven.de>"
    print "Date: %s" % (version_date)
    print ""


def print_usage():
    print "Datasource program to get data from Telekom speedport hybrid for Check_MK."
    print "Output will be printed in <<<local>>> section."
    print ""
    print_version()
    print "-H, --host    -> address/ip (mandatory)"
    print "-h, --help    -> guess what ;-)"
    print "-V, --version -> print version"
    print "-v            -> verbose"


# Process shell arguments
def main(argv):
    #pprint(sys.argv[1:])

    if (sys.argv[1:] == []):
        print "No arguments given!\n"
        print_usage()
        sys.exit(2)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hH:vV", ["help",
                                                          "version",
                                                          "host=",
                                                         ])
    except getopt.GetoptError as err:
        print str(err)  # will print something like "option -a not recognized"
        print_usage()
        sys.exit(2)

    global _debug,host
    _debug      = False
    host        = None

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_usage()
            sys.exit()
        if opt in ("-V", "--version"):
            print_version()
            sys.exit()
        elif opt == '-v':
            _debug = True
        elif opt in ("-H", "--host"):
            host = arg

    if (_debug == True): pprint(sys.argv[1:])


# Push commandline argument to main function to get parsed
if __name__ == "__main__":
    main(sys.argv[1:])


# Build some values
local_url = "http://%s/" % (host)
url       = "%sdata/Status.json" % (local_url)

if (_debug == True):
    print ""
    print "Host         : %s" % (host)
    print "url          : %s" % (url)
    print "local_url    : %s" % (local_url)


# Get output info from url and JSON loading
url_output = urllib.urlopen(url)
output = json.load(url_output)

if (_debug == True):
    print ""
    print "output\n: %s" % (output)


# Print agent section
print "<<<check_mk>>>"
print "Version: %s" % (version)
print "AgentOS: Linux"

print "<<<local>>>"

num_phones = 0
serviceprefix = "status_"


# Parse JSON info
for info in output:
    if(str(info['varvalue']).isdigit()) :
        perf = "value=" + info['varvalue']
    else:
        perf = "-"

    if info['varvalue'] == "":
        info['varvalue'] = "null"

    if "addphonenumber" == str(info['varid']):
        ph_phone_num = info['varvalue'][1]['varvalue']
        ph_failreason = info['varvalue'][2]['varvalue']
        ph_status = info['varvalue'][3]['varvalue']
        ph_voip_errno = info['varvalue'][4]['varvalue']
        print "0 %s %s %s" % (serviceprefix + "Phone_number_" + ph_phone_num,
                              "-",
                              "Status: " + ph_status + ", "
                              "Failreason: " + ph_failreason + ", "
                              "VOIP ErrNo: " + ph_voip_errno
                             )
    elif "adddect" == str(info['varid']):
        if num_phones < int(info['varvalue'][0]['varvalue']):
            num_phones = int(info['varvalue'][0]['varvalue'])
    else:
        print "0 %s %s %s" % (serviceprefix + info['varid'], perf, info['varvalue'])
    

print "0 %s %s %s" % (serviceprefix + "Registered_cordless_telephones", "phones=" + str(num_phones), num_phones)

print "<<<>>>"

