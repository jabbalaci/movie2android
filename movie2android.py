#!/usr/bin/env python

"""
movie2android
=============

* Author:  Laszlo Szathmary, 2013 (<jabba.laci@gmail.com>)
* Website: <https://ubuntuincident.wordpress.com/2013/02/26/resize-movies-for-androidios-with-ffmpeg/>
* GitHub:  <https://github.com/jabbalaci/movie2android>

Resize a movie for your Android/iOS device with ffmpeg.

You have two options:

(1) Get a static FFmpeg build from <http://ffmpeg.gusari.org/static/>.
It includes the audio codecs libvo_aacenc and aac. They are OK but not very good.

(2) If you want better codecs, you must compile your own FFmpeg,
as described here: <http://ubuntuincident.wordpress.com/2013/03/05/compile-your-own-ffmpeg/>.
It will include libfdk_aac and libfaac, where libfdk_aac is
considered to be the best.

In the config part of the script you must select
which FFmpeg version you have (set the variable VERSION).

This mini project was inspired by the LUD-Media-Converter
(<https://github.com/kunaldeo/LUD-Media-Converter>).

Usage:
------

    ./movie2android.py movie.avi [movie2.avi]...

It will resize the movie and produce a `movie.mp4` file.
If the input was called `movie.mp4`, the output will be
called `movie-resized.mp4`. You can change the ffmpeg settings
by adjusting the `config` dictionary in the source.

You can also pass *several* parameters to the script and they
will be processed one by one in a queue.

Accepted switches:

    -threads:<n>            default: -threads:2
"""

__author__ = "Laszlo Szathmary (jabba.laci@gmail.com)"
__version__ = "0.1.5"
__date__ = "20130321"
__copyright__ = "Copyright (c) 2013 Laszlo Szathmary"
__license__ = "GPL"

import os
import sys
import termcolor
import re
from texttable import Texttable
import utils

STATIC_BUILD, OWN_COMPILATION = range(2)    # enum
FAILED = "failed"

# select which version you have:
#VERSION = STATIC_BUILD
VERSION = OWN_COMPILATION

# all values are strings (even numeric values)
config = {
    'ffmpeg': '/opt/ffmpeg.static/ffmpeg',
    'bitrate': '600k',
    'width': '480',
    'height': '320',
    'threads': '2',
    'audio_codec': 'aac -strict experimental',
    'audio_codec_failsafe': 'libvo_aacenc',     # if the previous fails
}

if VERSION == OWN_COMPILATION:
    config['ffmpeg'] = 'ffmpeg'
    config['audio_codec'] = 'libfdk_aac'
    config['audio_codec_failsafe'] = 'libfaac'

FINGERPRINT = utils.get_short_fingerprint()
if FINGERPRINT == 'a7e7d4':
    # on my home desktop I want this to be the default
    config['threads'] = 4

def check_switches(args):
    """
    Process arguments and if there is a switch among them, modify
    the config part accordingly.

    Return value: argument list without switches.
    """
    global config
    #
    copy = []
    for e in args:
        m = re.search(r'^-threads:(\d+)$', e)
        if m:
            config['threads'] = m.group(1)
        else:
            copy.append(e)
    #
    return copy

sys.argv = check_switches(sys.argv)

command = """{ffmpeg} -i \"%(input)s\" -codec:v libx264 -quality good -cpu-used 0
-b:v {bitrate} -profile:v baseline -level 30 -y -maxrate 2000k
-bufsize 2000k -vf scale={width}:{height} -threads {threads} -codec:a %(audio_codec)s
-b:a 128k \"%(output)s\"""".replace('\n', ' ').format(**config)

audio_codec_problem = "Warning! There was a problem with the audio codec and the conversion failed. " + \
    "Retrying another method..."

#############################################################################
##  end of config  ##########################################################
#############################################################################

class Result(object):
    """
    A record to hold information about a converted video file.
    """
    def __init__(self, status=True):
        self.status = status    # True: OK, False: conversion failed
        self.file_name = None   # (str)
        self.file_size = 0      # (int)
        self.elapsed_time = 0.0 # (float)


def frame(fname, size_tuple):
    index, full_size = size_tuple
    t = utils.sec_to_hh_mm_ss(utils.get_video_length(fname))
    s = "({index} of {full_size}) {fname} ({time})".format(
        index=index, full_size=full_size, fname=fname, time=t
    )

    size = len(s)
    horizontal = '+' + '-' * (size+2) + '+'
    print termcolor.colored(horizontal, "green")
    print termcolor.colored('| ' + s + ' |', "green")
    print termcolor.colored(horizontal, "green")


def resize(fname, size_tuple):
    """
    Resize the current video file with ffmpeg.
    """
    if not os.path.isfile(fname):
        print termcolor.colored("Warning: the file {0} doesn't exist!".format(fname), "red")
        return Result(False)
    # else

    fileBaseName = os.path.splitext(fname)[0]
    output = fileBaseName+'.mp4'
    if os.path.isfile(output):
        output = "{0}-resized.mp4".format(fileBaseName)
    if os.path.isfile(output):
        print termcolor.colored('Warning: the file {0} exists!'.format(output), "red")
        return Result(False)

    # else
    result = Result()
    timer = utils.Timer()

    cmd = command % {'input': fname, 'output': output, 'audio_codec': config['audio_codec']}
    result.file_name = output
    print termcolor.colored(cmd, "green")
    frame(fname, size_tuple)
    with timer:
        exit_code = utils.call_and_get_exit_code(cmd)
    if exit_code == 0:
        print termcolor.colored("Success! Conversion time: {0:.1f} sec.".format(timer.elapsed_time()), "green")
        print '#'
        result.file_size = os.path.getsize(result.file_name)
        return result
    else:
        print termcolor.colored(audio_codec_problem, "red")
        os.unlink(output)
        cmd = command % {'input': fname, 'output': output, 'audio_codec': config['audio_codec_failsafe']}
        result.file_name = output
        print termcolor.colored(cmd, "green")
        frame(fname, size_tuple)
        with timer:
            exit_code = utils.call_and_get_exit_code(cmd)
        if exit_code == 0:
            print termcolor.colored("Success! Conversion time: {0:.1f} sec.".format(timer.elapsed_time()), "green")
            print '#'
            result.file_size = os.path.getsize(result.file_name)
            return result
        else:
            return Result(False)


def main(args):
    """
    process each argument
    """
    table = Texttable()
    table.set_cols_align(["r", "r", "r", "r", "r"])
    rows = [["Number", "File Name", "File Size", "Video Duration (H:MM:SS)", "Conversion Time"]]
    total_time = 0.0
    total_file_size = 0

    for index, arg in enumerate(args, start=1):
        timer = utils.Timer()
        with timer:
            result = resize(arg, (index, len(args)))
        #
        result.elapsed_time = timer.elapsed_time()
        rows.append([index,
                     result.file_name,
                     utils.sizeof_fmt(result.file_size),
                     utils.sec_to_hh_mm_ss(utils.get_video_length(result.file_name)) if result.file_name else "--",
                     "{0:.1f} sec.".format(result.elapsed_time) if result.status else FAILED])
        #
        if rows[-1][-1] != FAILED:
            total_time += result.elapsed_time
        total_file_size += result.file_size

    table.add_rows(rows)
    print table.draw()
    print 'Total file size:', utils.sizeof_fmt(total_file_size)
    print 'Total time: {0} (H:MM:SS)'.format(utils.sec_to_hh_mm_ss(total_time))
    print utils.get_unix_date()

#############################################################################

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: {0} <movie>".format(os.path.split(sys.argv[0])[1])
        sys.exit(1)
    else:
        main(sys.argv[1:])
