streamscrobbler-python
======================

The python class used on Dirble.com to get titles and bitrates on streams.


### dependencies
streamscrobbler is mostly using urllib2, httplib and urlparse. So this need to be isntalled or you'll get errors.


### How to use it
The class have around 3 fucntions you can use to get information from the stream. This will make it easier later with just one function to call.

in the example. remember to send in a array with stream id and such of a station to the worker function. And create a updatestatus function to save metadata to database.
```Python
import sys
import httplib2 as http
import httplib
import json
import math
import urllib2
import contextlib
import MySQLdb as mdb
import datetime
import time
import re

from time import sleep
from urlparse import urlparse

import multiprocessing

from streamscrobbler import streamscrobbler

streamscrobbler = streamscrobbler()

h = http.Http()

jobs = []

## this is words you dont want to be saved in db
blocklist = []
blocklist.append("Radionomy")
blocklist.append("Vol.")
blocklist.append("Vol")
blocklist.append("2014)")
blocklist.append("2012)")
blocklist.append("2013)")
blocklist.append("2011)")
blocklist.append("2010)")
blocklist.append("Episode")
blocklist.append("Ep")
blocklist.append("Viet Live Radio")
blocklist.append("Amandoi")
blocklist.append("Radio Show")
blocklist.append("WAMU")
blocklist.append("BreakZ.us")
blocklist.append("(PrisonPlanet.tv)")
blocklist.append("(PrisonPlanet.com)")
blocklist.append("(Infowars.net)")
blocklist.append("Rhythm86.com")
blocklist.append("jazzfm.com")
blocklist.append("NRJ")
blocklist.append("181.fm")
blocklist.append("Ad Break")
blocklist.append("Chromanova.fm proudly presents")
blocklist.append("The Hitz Channel")
blocklist.append("Radio SRF 1")

def worker(row):
	## row is a row form a table, with station information like streamurl and stationid.
	status = 0
	songtitle = None
	print "	Station: " + row[1]
	if row[2].endswith('.pls') or row[2].endswith('listen.pls?sid=1'):
		address = streamscrobbler.checkPLS(row[2])
	else:
		address = row[2]
	if isinstance(address, str):
		meta_interval = streamscrobbler.checkWhatServer(address)
	else:
		meta_interval = bool(0)
	if isinstance(meta_interval, bool):
		if meta_interval is True:
			status = 1
		else:
			status = 0
		metadata = False;
	elif "SHOUTcast" in meta_interval:
		status = 1
		if "1.9" in meta_interval:
			metadata = streamscrobbler.shoutcastOldGet(address, False);
		else:
			metadata = streamscrobbler.shoutcastCheck(address, False);
	elif "Icecast" or "137" in meta_interval:
		status = 1
		metadata = streamscrobbler.shoutcastCheck(address, True);
	elif "StreamMachine" in meta_interval:
		status = 1
		metadata = streamscrobbler.shoutcastCheck(address, True);
	else:
		metadata = False;
	if metadata is not False:
		status = 2
	print '	finish with status: ' + str(status);
	if metadata is not False:
		print "	bitrate: " + str(metadata.get("bitrate"));
		if metadata.get("song") != "" and " - " in metadata.get("song"):
			songtitle = metadata.get("song")
	if status == 0:
		print "	Server is down."
	if 'songtitle' in locals():
		if songtitle is not None:
				print "	Songtitle: " + songtitle;
	if songtitle is None:
		result = updateStatus(status, None, None, row[0])
	else:
		song = songtitle.split(" - ", 1 )
		
		blocklist.append(row[1])
		blocklist.append(row[1].replace(" ", ""))
		blocklist.append(row[1].replace("Radio", "").replace("|", "").replace(" ", ""))
		blocklist.append(row[1] + ".com")
		blocklist.append(row[1] + ".tv")
		blocklist.append(row[1] + ".net")
		blocklist.append(row[1].replace(" ", "") + ".com")
		blocklist.append(row[1].replace(" ", "") + ".tv")
		blocklist.append(row[1].replace(" ", "") + ".net")
		
		if not any(s in song[0] for s in blocklist) and not any(s in song[1] for s in blocklist):
			if song[0] != song[1] and song[0] != "" and song[1] != "" and song[0] != row[1] and song[1] != row[1]:
				## updatestatus is a function to just save metadata to the database. no weird stuff there.
				result = updateStatus(status, song[1], song[0], row[0])
			else:
				print "	empty artist or songtitle or metadata was stationname"
		else:
			print "	containing blockwords or stationname, not added."
		
		blocklist.remove(row[1])
		blocklist.remove(row[1].replace(" ", ""))
		blocklist.remove(row[1].replace("Radio", "").replace("|", "").replace(" ", ""))
		blocklist.remove(row[1] + ".com")
		blocklist.remove(row[1] + ".tv")
		blocklist.remove(row[1] + ".net")
		blocklist.remove(row[1].replace(" ", "") + ".com")
		blocklist.remove(row[1].replace(" ", "") + ".tv")
		blocklist.remove(row[1].replace(" ", "") + ".net")
	
	print '	----------------------------';
			
	metadata = False
```