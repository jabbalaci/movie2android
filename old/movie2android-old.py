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
        output = "{0}-resized.mp4".format(fileBaseName)
    if os.path.isfile(output):
        print termcolor.colored('Warning: the file {0} exists!'.format(output), "red")
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
        print "Usage: {0} <movie>".format(os.path.split(sys.argv[0])[1])
        sys.exit(1)
    else:
        main(sys.argv[1:])
