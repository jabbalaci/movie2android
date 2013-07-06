#!/usr/bin/env python

import socket
import select
import config as cfg
import Queue
from threading import Thread
import sys
import os


class ProcessThread(Thread):
    def __init__(self):
        super(ProcessThread, self).__init__()
        self.running = True
        self.q = Queue.Queue()

    def add(self, data):
        self.q.put(data)

    def stop(self):
        self.running = False

    def run(self):
        q = self.q
        while self.running:
            try:
                value = q.get(block=True, timeout=1)
                process(value)
            except Queue.Empty:
                sys.stdout.write('.')
                sys.stdout.flush()
        #
        if not q.empty():
            print "Elements left in the queue:"
            while not q.empty():
                print q.get()

t = ProcessThread()
t.start()


def process(value):
    cmd = '{m2a} "{f}"'.format(m2a=cfg.M2A, f=value)
    print '#', cmd
    os.system(cmd)


def main():
    s = socket.socket()         # Create a socket object
    host = socket.gethostname() # Get local machine name
    port = cfg.PORT                # Reserve a port for your service.
    s.bind((host, port))        # Bind to the port
    print "Listening on port {p}...".format(p=port)

    s.listen(5)                 # Now wait for client connection.
    while True:
        try:
            client, addr = s.accept()
            ready = select.select([client,],[], [],2)
            if ready[0]:
                data = client.recv(4096)
                #print data
                t.add(data)
        except KeyboardInterrupt:
            print
            print "Stop."
            break
        except socket.error, msg:
            print "Socket error! %s" % msg
            break
    #
    cleanup()


def cleanup():
    t.stop()
    t.join()

#############################################################################

if __name__ == "__main__":
    main()
