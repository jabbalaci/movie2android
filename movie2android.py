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

    ./movie2android.py movie.avi

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
__version__ = "0.1.2"
__date__ = "20130305"
__copyright__ = "Copyright (c) 2013 Laszlo Szathmary"
__license__ = "GPL"

import os
import sys
import termcolor
import shlex
from subprocess import Popen, PIPE
import re
#import pprint

STATIC_BUILD = 1
OWN_COMPILATION = 2

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

command = """{ffmpeg} -i \"%(input)s\" -codec:v libx264 -quality good -cpu-used 0
-b:v {bitrate} -profile:v baseline -level 30 -y -maxrate 2000k
-bufsize 2000k -vf scale={width}:{height} -threads {threads} -codec:a %(audio_codec)s
-b:a 128k \"%(output)s\"""".replace('\n', ' ').format(**config)

audio_codec_problem = "Warning! There was a problem with the audio codec and the conversion failed. " + \
    "Retrying another method..."


def call_and_get_exit_code(cmd):
    process = Popen(shlex.split(cmd), stdout=PIPE)
    process.communicate()
    return process.wait()


def resize(fname):
    """
    Resize the current video file with ffmpeg.
    """
    fileBaseName = os.path.splitext(fname)[0]
    output = fileBaseName+'.mp4'
    if os.path.isfile(output):
        output = "{0}-resized.mp4".format(fileBaseName)
    if os.path.isfile(output):
        print termcolor.colored('Warning: the file {0} exists!'.format(output), "red")
        return
    # else
    cmd = command % {'input': fname, 'output': output, 'audio_codec': config['audio_codec']}
    print termcolor.colored(cmd, "green")
    exit_code = call_and_get_exit_code(cmd)
    if exit_code == 0:
        print termcolor.colored("Success!", "green")
    else:
        print termcolor.colored(audio_codec_problem, "red")
        os.unlink(output)
        cmd = command % {'input': fname, 'output': output, 'audio_codec': config['audio_codec_failsafe']}
        print termcolor.colored(cmd, "green")
        exit_code = call_and_get_exit_code(cmd)
        if exit_code == 0:
            print termcolor.colored("Success!", "green")


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


def main(args):
    """
    process each argument
    """
    args = check_switches(args)
    #
    for arg in args:
        resize(arg)

#############################################################################

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: {0} <movie>".format(os.path.split(sys.argv[0])[1])
        sys.exit(1)
    else:
        main(sys.argv[1:])
