#!/usr/bin/env python

import re
import platform as p
import uuid
import hashlib
import time
import shlex
from subprocess import Popen, PIPE, STDOUT
from datetime import timedelta

video_info = "/usr/bin/mplayer '{0}' -ao null -vo null -frames 1 -identify"


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


def sizeof_fmt(num):
    """
    Convert file size to human readable format.
    """
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "{0:.2f} {1}".format(num, x)
        num /= 1024.0


def get_simple_cmd_output(cmd, stderr=STDOUT):
    """
    Execute a simple external command and get its output.

    The command contains no pipes. Error messages are
    redirected to the standard output by default.
    """
    args = shlex.split(cmd)
    return Popen(args, stdout=PIPE, stderr=stderr).communicate()[0]


def get_video_info(video_file):
    """
    Get info about a video.

    The info is returned by mplayer. The result is a
    dictionary whose keys start with 'ID_'.
    """
    cmd = video_info.format(video_file)
    output = get_simple_cmd_output(cmd)
    return dict(re.findall('(ID_.*)=(.*)', output))


def get_video_length(video_file):
    """
    Get the length of a video in seconds.

    The length is extracted with mplayer.
    The return value is a real number.
    """
    info = get_video_info(video_file)
    return float(info['ID_LENGTH'])


def sec_to_hh_mm_ss(seconds, as_str=True):
    """
    Convert a time given in seconds to H:MM:SS format.

    If as_str is True, the return value is a string.
    If as_str is False, the return value is a tuple (H:MM:SS).
    """
    s = str(timedelta(seconds=int(round(seconds))))
    if as_str:
        return s
    else:
        return tuple([int(x) for x in s.split(':')])

#############################################################################

if __name__ == "__main__":
    print get_fingerprint(True)
    print get_short_fingerprint()
    print get_video_length("/opt/shared.folder.vbox/video/Keynote_ Guido Van Rossum.mp4")
