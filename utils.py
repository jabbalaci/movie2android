#!/usr/bin/env python

import platform as p
import uuid
import hashlib
import time
import shlex
from subprocess import Popen, PIPE


class Timer(object):

    def __enter__(self):
        self.__start = time.time()

    def __exit__(self, type, value, traceback): #@ReservedAssignment
        # Error handling here
        self.__finish = time.time()

    def elapsed_time(self):
        return self.__finish - self.__start


def string_to_md5(content):
    """Calculate the md5 hash of a string.

    This 'string' can be the binary content of a file too."""
    return hashlib.md5(content).hexdigest()


def get_fingerprint(md5=False):
    """
    Fingerprint of the current operating system/platform.

    If md5 is True, a digital fingerprint is returned.
    """
    sb = []
    sb.append(p.node())
    sb.append(p.architecture()[0])
    sb.append(p.architecture()[1])
    sb.append(p.machine())
    sb.append(p.processor())
    sb.append(p.system())
    sb.append(str(uuid.getnode()))    # MAC address
    text = '#'.join(sb)
    if md5:
        return string_to_md5(text)
    else:
        return text


def get_short_fingerprint(length=6):
    """
    A short digital fingerprint of the current operating system/platform.

    Length should be at least 6 characters.
    """
    assert 6 <= length <= 32
    #
    return get_fingerprint(md5=True)[-length:]


def call_and_get_exit_code(cmd):
    process = Popen(shlex.split(cmd), stdout=PIPE)
    process.communicate()
    return process.wait()

#############################################################################

if __name__ == "__main__":
    print get_fingerprint(True)
    print get_short_fingerprint()
