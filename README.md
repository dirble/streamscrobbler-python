streamscrobbler-python
======================

This python module gets the metadata and song played on a stream. The metadata is content-type (mpeg, ACC, ACC+), 
bitrate and played song. It has support to handling pls files directly for now.


### Dependencies
* Python 3.5

### Streams supported
Supports the following streamtypes:

* Shoutcast
* Icecast
* probably other custom made that use icy-metaint

And also different stream services:

* Radionomy
* Streammachine
* tunein

### How to use it
You use one function to get a dictionary of status and metadata.
metadata is a dictionary of bitrate, content-type and songtitle.

See how to call it under here:
```Python
from streamscrobbler import streamscrobbler

##streamurl can be a url directly to the stream or to a pls file
streamurl = "http://somafm.com/seventies.pls"
stationinfo = streamscrobbler.get_server_info(streamurl)
##metadata is the bitrate and current song
metadata = stationinfo["metadata"]
```
