#!/usr/bin/env python

"""
Resize a movie for your Android/iOS device with ffmpeg.

Get a static FFmpeg build from http://ffmpeg.gusari.org/static/ .

This mini project was inspired by the LUD-Media-Converter
(https://github.com/kunaldeo/LUD-Media-Converter).

by Jabba Laci (jabba.laci@gmail.com), 2013
"""

import os
import sys
import termcolor
from jinja2 import Environment


config = {
    'ffmpeg': '/opt/ffmpeg.static/ffmpeg',
    'bitrate': '600k',
    'width': '480',
    'height': '320',
    'threads': '2'
}

command = """{{ ffmpeg }} -i {input} -codec:v libx264 -quality good -cpu-used 0
-b:v {{ bitrate }} -profile:v baseline -level 30 -y -maxrate 2000k
-bufsize 2000k -vf scale={{ width }}:{{ height }} -threads {{ threads }} -codec:a libvo_aacenc
-b:a 128k {output}""".replace('\n', ' ')

command = Environment().from_string(command).render(config)


def resize(fname):
    """
    Resize the current video file with ffmpeg.
    """
    fileBaseName = os.path.splitext(fname)[0]
    output = fileBaseName+'.mp4'
    if os.path.isfile(output):
        output = "{}-resized.mp4".format(fileBaseName)
    if os.path.isfile(output):
        print termcolor.colored('Warning: the file {} exists!'.format(output), "red")
        return
    # else
    cmd = command.format(input=fname, output=output)
    print termcolor.colored(cmd, "green")
    os.system(cmd)


def main(movies):
    """process each argument"""
    for movie in movies:
        resize(movie)

#############################################################################

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: {} <movie>".format(sys.argv[0])
        sys.exit(1)
    else:
        main(sys.argv[1:])
