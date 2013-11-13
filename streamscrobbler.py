#!/usr/bin/python
# -*- coding: utf-8 -*-
import httplib2 as http
import httplib
from urlparse import urlparse
import urllib2
class streamscrobbler:
	def parse_headers(self, response):
		headers = {}
		int = 0
		while True:
			line = response.readline()
			if line == '\r\n':
				break  # end of headers
			if ':' in line:
				key, value = line.split(':', 1)
				headers[key] = value
			if int == 12:
				break;
			int = int + 1
		return headers
	
	
	def checkWhatServer(self, address):
		try:
			status = urllib2.urlopen(address, timeout=2).getcode()
		except Exception:
			return bool(0)
			
		if status == 200:
			request = urllib2.Request(address)
			request.add_header('icy-metadata', 1)
			try:
				response = urllib2.urlopen(request, timeout=6)
				if "server" in response.headers:
					shoutcast = response.headers['server']
				elif "X-Powered-By" in response.headers:
					shoutcast = response.headers['X-Powered-By']
				else:
					headers = self.parse_headers(response)
					if "icy-notice1" in headers:
						shoutcast = headers['icy-notice1']
						if "This stream requires" in shoutcast:
							shoutcast = headers['icy-notice2']
					else:
						shoutcast = bool(1);
				response.close()
			except Exception:
				return bool(1)
		else:
			shoutcast = bool(0);
			
		return shoutcast;
	
	
	def checkPLS(self, address):
		try:
			response = urllib2.urlopen(address, timeout=2)
			for line in response:
				if line.startswith("File1="):
					stream = line;
				
			response.close()
			if 'stream' in locals():
				return stream[6:]
			else:
				return bool(0)
		except Exception:
			return bool(0)
	
	def shoutcastOldGet(self, address, itsOld):
		station = self.shoutcast7htmlCheck(address)
		if station is False:
			station = self.shoutcastCheck(address, itsOld)
		
		return station;
		
	def shoutcast7htmlCheck(self, address):
		
		o = urlparse(address)
		stringurl = o.scheme + "://" + o.netloc + "/7.html"
		user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
		request = urllib2.Request(stringurl)
		request.add_header('User-Agent', user_agent)
		try:
			response = urllib2.urlopen(request, timeout=2)
			for line in response:
				line = self.stripTags(line)
				lines = line.split(',', 7)
				if len(lines) > 1:
					response.close()
					return {'song':lines[6], 'bitrate':lines[5]}
				else:
					response.close()
					return False
			else:
				response.close()
		except Exception, err:
			print "	Error 7.html: " + err
			return False
	
	
	def shoutcastCheck(self, address, itsOld):
		request = urllib2.Request(address)
		try:
			request.add_header('icy-metadata', 1)
			response = urllib2.urlopen(request, timeout=5)
			if itsOld is not True:
				headers = self.parse_headers(response)
				bitrate = headers['icy-br']
				icy_metaint_header = headers['icy-metaint']
			else:
				bitrate = response.headers.get('icy-br').split(",")[0]
				icy_metaint_header = response.headers.get('icy-metaint')
			if icy_metaint_header is not None:
				metaint = int(icy_metaint_header)
				read_buffer = metaint + 255
				content = response.read(read_buffer)
				
				start = "StreamTitle='"
				end = "';"
				
				title = re.search('%s(.*)%s' % (start, end), content[metaint:]).group(1)
				title = re.sub("StreamUrl='.*?';", "", title).replace("';", "").replace("StreamUrl='", "")
				title = re.sub("&artist=.*", "", title)
				title = re.sub("http://.*", "", title)
				
				response.close()
				return {'song':title, 'bitrate':bitrate}
			else:
				response.close()
				print "No metaint"
		except Exception, err:
			print "	Error"
			return False

	def stripTags(self, text):
         finished = 0
         while not finished:
             finished = 1
             start = text.find("<")
             if start >= 0:
                 stop = text[start:].find(">")
                 if stop >= 0:
                     text = text[:start] + text[start + stop + 1:]
                     finished = 0
         return text
