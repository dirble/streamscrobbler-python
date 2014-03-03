streamscrobbler-python
======================

The python class used on Dirble.com to get titles and bitrates on streams.


### dependencies
streamscrobbler is mostly using urllib2, httplib and urlparse. So this need to be isntalled or you'll get errors.


### How to use it
You use one function to get a object of status and metadata.
status is a integer of 0,1,2 - 0 is down, 1 is up, 2 is up with metadata
metadata is a object of bitrate, content-type and songtitle.

See how to call it under here:
```Python
from streamscrobbler import streamscrobbler
streamscrobbler = streamscrobbler()

##streamurl can be a url directly to the stream or to a pls file. Support for m3u is coming soon.
streamurl = "http://217.198.148.101:80/"
stationinfo = streamscrobbler.getServerInfo(streamurl)
##metadata is the bitrate and current song
metadata = stationinfo.get("metadata")
## status is the integer to tell if the server is up or down, 0 means down, 1 up, 2 means up but also got metadata.
status = stationinfo.get("status")
```