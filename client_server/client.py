#!/usr/bin/env python

import config as cfg
import sys
import socket
import os


def main(elems):
    try:
        for e in elems:
            fname = os.path.abspath(e)
            if not os.path.isfile(fname):
                print "Warning: {f} is not a file.".format(f=fname)
                continue
            # else
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host = socket.gethostname()
            client.connect((host, cfg.PORT))
            client.send(fname)
            client.shutdown(socket.SHUT_RDWR)
            client.close()
    except Exception as msg:
        print msg

#############################################################################

if __name__ == "__main__":
    main(sys.argv[1:])
