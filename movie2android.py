#!/usr/bin/env python

"""
movie2android
=============

* Author:  Laszlo Szathmary, 2013 (<jabba.laci@gmail.com>)
* Website: <https://ubuntuincident.wordpress.com/2013/02/26/resize-movies-for-androidios-with-ffmpeg/>
* GitHub:  <https://github.com/jabbalaci/movie2android>

Resize a movie for your Android/iOS device with ffmpeg.

Get a static FFmpeg build from <http://ffmpeg.gusari.org/static/>.

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
"""

__author__ = "Laszlo Szathmary (jabba.laci@gmail.com)"
__version__ = "0.1.1"
__date__ = "20130303"
__copyright__ = "Copyright (c) 2013 Laszlo Szathmary"
__license__ = "GPL"

import os
import sys
import termcolor
import shlex
from subprocess import Popen, PIPE


config = {
    'ffmpeg': '/opt/ffmpeg.static/ffmpeg',
    'bitrate': '600k',
    'width': '480',
    'height': '320',
    'threads': '2'
}
AUDIO_CODEC_DEFAULT = 'libvo_aacenc'
AUDIO_CODEC_FAILSAFE = 'copy'    # if the previous fails

command = """{ffmpeg} -i %(input)s -codec:v libx264 -quality good -cpu-used 0
-b:v {bitrate} -profile:v baseline -level 30 -y -maxrate 2000k
-bufsize 2000k -vf scale={width}:{height} -threads {threads} -codec:a %(audio_codec)s
-b:a 128k %(output)s""".replace('\n', ' ').format(**config)

audio_codec_problem = "Warning! There was a problem with the audio codec and the conversion failed. " + \
    "Retrying another method..."

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
    cmd = command % {'input': fname, 'output': output, 'audio_codec': AUDIO_CODEC_DEFAULT}
    print termcolor.colored(cmd, "green")
    process = Popen(shlex.split(cmd), stdout=PIPE)
    process.communicate()
    exit_code = process.wait()
    if exit_code != 0:
        print termcolor.colored(audio_codec_problem, "red")
        os.unlink(output)
        cmd = command % {'input': fname, 'output': output, 'audio_codec': AUDIO_CODEC_FAILSAFE}
        print termcolor.colored(cmd, "green")
        process = Popen(shlex.split(cmd), stdout=PIPE)
        process.communicate()
        exit_code = process.wait()
        if exit_code == 0:
            print termcolor.colored("Success!", "green")


def main(movies):
    """process each argument"""
    for movie in movies:
        resize(movie)

#############################################################################

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: {0} <movie>".format(os.path.split(sys.argv[0])[1])
        sys.exit(1)
    else:
        main(sys.argv[1:])
