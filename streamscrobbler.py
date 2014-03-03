#!/usr/bin/python
# -*- coding: utf-8 -*-
import httplib2 as http
import httplib
import re
from urlparse import urlparse
import pprint
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
    
    # this is the fucntion you should call with the url to get all data sorted as a object in the return
    def getServerInfo(self, url):
        status = 0
        if url.endswith('.pls') or url.endswith('listen.pls?sid=1'):
            address = self.checkPLS(url)
        else:
            address = url
        if isinstance(address, str):
            meta_interval = self.checkWhatServer(address)
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
                metadata = self.shoutcastOldGet(address, False);
            else:
                metadata = self.shoutcastCheck(address, False);
        elif "Icecast" or "137" in meta_interval:
            status = 1
            metadata = self.shoutcastCheck(address, True);
        elif "StreamMachine" in meta_interval:
            status = 1
            metadata = self.shoutcastCheck(address, True);
        else:
            metadata = False;
        
        return {"status":status, "metadata":metadata}
    
    
    def checkWhatServer(self, address):
        try:
            status = urllib2.urlopen(address, timeout=2).getcode()
        except Exception:
            return bool(0)
        
        if status == 200:
            request = urllib2.Request(address)
            user_agent = 'iTunes/9.1.1'
            request.add_header('User-Agent', user_agent)
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
        else:
            station = self.justgetcontenttype(address, station)
        
        return station;
    
    def shoutcast7htmlCheck(self, address):
        o = urlparse(address)
        stringurl = o.scheme + "://" + o.netloc + "/7.html"
        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        request = urllib2.Request(stringurl)
        request.add_header('User-Agent', user_agent)
        request.add_header('Accept-Charset', 'utf-8')
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
        except urllib2.HTTPError, e:
            print '    Error 7.html, HTTPError = ' + str(e.code)
            return False
        except urllib2.URLError, e:
            print "    Error 7.html, URLError: " + str(e.reason)
            return False
        except Exception, err:
            print "    Error 7.html"
            return False
    
    def justgetcontenttype(self, address, station):
        request = urllib2.Request(address)
        try:
            user_agent = 'iTunes/9.1.1'
            request.add_header('User-Agent', user_agent)
            request.add_header('icy-metadata', 1)
            request.add_header('Accept-Charset', 'utf-8')
            response = urllib2.urlopen(request, timeout=5)
            
            contenttype = "?" 
            
            headers = self.parse_headers(response)
            if "Content-Type" in headers:
                contenttype = headers['Content-Type']
            elif 'content-type' in headers:
                contenttype = headers['content-type']
                
            response.close()
            
            return {'song':station.get("song"), 'bitrate':station.get("bitrate"), 'contenttype':contenttype}
        except urllib2.HTTPError, e:
            print '    Error, HTTPError = ' + str(e.code)
            return False
        except urllib2.URLError, e:
            print "    Error, URLError: " + str(e.reason)
            return False
        except Exception, err:
            print "    Error: " +str(err)
            return False
        
    
    def shoutcastCheck(self, address, itsOld):
        request = urllib2.Request(address)
        try:
            user_agent = 'iTunes/9.1.1'
            request.add_header('User-Agent', user_agent)
            request.add_header('icy-metadata', 1)
            request.add_header('Accept-Charset', 'utf-8')
            response = urllib2.urlopen(request, timeout=5)
            
            if itsOld is not True:
                headers = self.parse_headers(response)
                bitrate = headers['icy-br']
                icy_metaint_header = headers['icy-metaint']
                if "Content-Type" in headers:
                    contenttype = headers['Content-Type']
                elif 'content-type' in headers:
                    contenttype = headers['content-type']
            else:
                bitrate = response.headers.get('icy-br').split(",")[0]
                icy_metaint_header = response.headers.get('icy-metaint')
                
            if response.headers.get('Content-Type') is not None:
                contenttype = response.headers.get('Content-Type')
            elif response.headers.get('content-type') is not None:
                contenttype = response.headers.get('content-type')
            
            print response.headers

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
                return {'song':title, 'bitrate':bitrate, 'contenttype':contenttype}
            else:
                response.close()
                print "No metaint"
        except urllib2.HTTPError, e:
            print '    Error, HTTPError = ' + str(e.code)
            return False
        except urllib2.URLError, e:
            print "    Error, URLError: " + str(e.reason)
            return False
        except Exception, err:
            print "    Error: " +str(err)
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