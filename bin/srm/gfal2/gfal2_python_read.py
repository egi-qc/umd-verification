#!/usr/bin/python
# -*- coding: utf-8 -*-
##
# Example : open/read/close a file with gfal 2.0
#

import os
import string
import sys

import gfal2


# main func
if __name__ == '__main__':
    # comment for usage
    if (len(sys.argv) < 2):
        print("""
            Usage\t %s [gfal_url]
                Example: %s lfn:/grid/dteam/myfile
                         %s srm://myserver.com/myhome/myfile
        """ % (sys.argv[0], sys.argv[0], sys.argv[0]))
        os._exit(1)

    ctx = gfal2.creat_context()
    # open the file
    f = ctx.open(sys.argv[1], 'r')
    # read first 10 bytesthe max_size first bytes.
    content = f.read(10)
    # Hex dump
    str = []
    for byte in content:
        print("%2X " % ord(byte))
        if byte in string.printable:
            str.append(byte)
        else:
            str.append('.')
    print('\t', ' '.join(str))
