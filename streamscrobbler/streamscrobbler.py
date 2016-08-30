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
                headers[key] = value.rstrip()
            if int == 12:
                break;
            int = int + 1
        return headers


    # this is the fucntion you should call with the url to get all data sorted as a object in the return
    def getServerInfo(self, url):
        print
        "shoutcast check v.2"

        if url.endswith('.pls') or url.endswith('listen.pls?sid=1'):
            address = self.checkPLS(url)
        else:
            address = url
        if isinstance(address, str):
            meta_interval = self.getAllData(address)
        else:
            meta_interval = {"status": 0, "metadata": None}

        return meta_interval

    def getAllData(self, address):
        shoutcast = False
        status = 0

        request = urllib2.Request(address)
        user_agent = 'iTunes/9.1.1'
        request.add_header('User-Agent', user_agent)
        request.add_header('icy-metadata', 1)
        try:
            response = urllib2.urlopen(request, timeout=6)
            headers = self.getHeaders(response)
            pp = pprint.PrettyPrinter(indent=4)
            print "parse headers: "
            pp.pprint(headers)
                
            if "server" in headers:
                shoutcast = headers['server']
            elif "X-Powered-By" in headers:
                shoutcast = headers['X-Powered-By']
            elif "icy-notice1" in headers:
                shoutcast = headers['icy-notice2']
            else:
                shoutcast = bool(1)

            if isinstance(shoutcast, bool):
                if shoutcast is True:
                    status = 1
                else:
                    status = 0
                metadata = False;
            elif "SHOUTcast" in shoutcast:
                status = 1
                metadata = self.shoutcastCheck(response, headers, False)
            elif "Icecast" or "137" in shoutcast:
                status = 1
                metadata = self.shoutcastCheck(response, headers, True)
            elif "StreamMachine" in shoutcast:
                status = 1
                metadata = self.shoutcastCheck(response, headers, True)
            elif shoutcast is not None:
                status = 1
                metadata = self.shoutcastCheck(response, headers, True)
            else:
                metadata = False
            response.close()
            return {"status": status, "metadata": metadata}

        except urllib2.HTTPError, e:
            print '    Error, HTTPError = ' + str(e.code)
            return {"status": status, "metadata": None}

        except urllib2.URLError, e:
            print "    Error, URLError: " + str(e.reason)
            return {"status": status, "metadata": None}

        except Exception, err:
            print "    Error: " + str(err)
            return {"status": status, "metadata": None}


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


    def shoutcastCheck(self, response, headers, itsOld):
        if itsOld is not True:
            if 'icy-br' in headers:
                bitrate = headers['icy-br']
                bitrate = bitrate.rstrip()
            else:
                bitrate = None

            if 'icy-metaint' in headers:
                icy_metaint_header = headers['icy-metaint']
            else:
                icy_metaint_header = None

            if "Content-Type" in headers:
                contenttype = headers['Content-Type']
            elif 'content-type' in headers:
                contenttype = headers['content-type']
                
        else:
            if 'icy-br' in headers:
                bitrate = headers['icy-br'].split(",")[0]
            else:
                bitrate = None
            if 'icy-metaint' in headers:
                icy_metaint_header = headers['icy-metaint']
            else:
                icy_metaint_header = None

        if headers.get('Content-Type') is not None:
            contenttype = headers.get('Content-Type')
        elif headers.get('content-type') is not None:
            contenttype = headers.get('content-type')

        if icy_metaint_header is not None:
            metaint = int(icy_metaint_header)
            print "icy metaint: " + str(metaint)
            read_buffer = metaint + 255
            content = response.read(read_buffer)

            start = "StreamTitle='"
            end = "';"

            try: 
                title = re.search('%s(.*)%s' % (start, end), content[metaint:]).group(1)
                title = re.sub("StreamUrl='.*?';", "", title).replace("';", "").replace("StreamUrl='", "")
                title = re.sub("&artist=.*", "", title)
                title = re.sub("http://.*", "", title)
                title.rstrip()
            except Exception, err:
                print "songtitle error: " + str(err)
                title = content[metaint:].split("'")[1]

            return {'song': title, 'bitrate': bitrate, 'contenttype': contenttype.rstrip()}
        else:
            print
            "No metaint"
            return False

    def getHeaders(self, response):
        if self.is_empty(response.headers.dict) is False:
            headers = response.headers.dict
        elif hasattr(response.info(),"item") and self.is_empty(response.info().item()) is False:
            headers = response.info().item()
        else:
            headers = self.parse_headers(response)
        return headers

    def is_empty(self, any_structure):
        if any_structure:
            return False
        else:
            return True
        

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