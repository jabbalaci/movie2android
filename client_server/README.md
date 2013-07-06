Scenario
========

You have lots of movies in *different* directories that you want to
convert to MP4 one after the other.

Server
------

There is a server listening to a dedicated port. It receives AVI
filenames with absolute paths and adds them to a queue. The
elements in the queue are processed by `movie2android.py` one
by one.

Client
------

When you have an AVI file that you want to convert to MP4, just 
add it to the processing queue with the client. The server receives
it and it will be processed.

Usage
-----

I suggest adding symbolic links to the server and the client:

    $ cd ~/bin    # make sure ~/bin is in your PATH
    $ ln -s .../server.py m2a_server.py
    $ ln -s .../client.py m2a_add

Then, start the server in a terminal and leave it running:

    $ m2a_server.py
    Listening on port 3030...
    ........

Find the movie file you want to convert and send it to the server.
You can pass as many movies to the server as you want.

    $ m2a_add movie.avi
