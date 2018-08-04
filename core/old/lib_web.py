#!/usr/bin/env python2
##
## web.py
## 1.0.7
##
## Copyright (C) 2011 - J4ckB
##
## This is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
##
## This is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## web is a python module to simplify multithread use of httplib
##

import httplib as h, urllib as u, threading, time, re
import urllib, sys
from threading import Thread

__version__ = '1.0.9'
__doc__ = "Version 1.0.9 by J4ckB\n\
    This module try to simplify use of httplib in single and multithread context\n\
    adding the ability to parse the result of an http connection with regular expression\n\
    and operate a sort of automagic configuration for dumb tasks.\n\
    Global Variables:\n\
    HTTP_TIMEOUT\tSet HTTP connection timeout in seconds (default: 5 secs)\n\
    _DEBUG      \tOnly for internal use and debug purpose, set it to 1 if you want some extra (verbose) info\n\
    Actually it supports the following HTTP/HTTPS Methods:\n\
    GET PUT HEAD POST DELETE TRACE OPTIONS CONNECT PATCH\n\
    \n\
    1.0.0: First version\n\
    1.0.2: Minor improvements\n\
    1.0.4: Improving error reporting in Web Class\n\
    1.0.6: modfied linkparser() method optimizing regular expressions\
    1.0.7: modified download() to set optional hook for progress bars\
    1.0.8: added some methods to WebResult in order to retrieve easily headers,body and so\
    1.0.9: addedd self.errors and method lastError() to read internal error"

_DEBUG = 0
_SUPPORTED_METHODS = ('GET', 'PUT', 'HEAD', 'POST', 'DELETE', 'TRACE', 'OPTIONS', 'CONNECT', 'PATCH')
HTTP_TIMEOUT = 5
WEB_REM_FILE_NAME = None
OLDTIME = None
OLDSIZE = None
OTIME = None

if __name__ == '__main__':
    print
    "-------------------------------------------------"
    print
    "Hallo! This is module WEB ", __version__
    print
    "!! Python modules can be used with 'import' !! "
    print
    "Please for help use help(web)"
    print
    "Have fun!"
    print
    "-------------------------------------------------"
    print
    "GNU Public Licens v3.0 -- Written by [j4ckb]     "
    print
    "-------------------------------------------------"
    quit(-1)
else:
    pass


class Web(Thread):
    __doc__ = 'Implementation of a Web connection\n'
    _HTTP_TIMEOUT = HTTP_TIMEOUT

    def __init__(self, linkstring='http://localhost:80/', method='GET', body=None, headers={}):
        """ Initialize the object, if linkstring is only an hostname will be used like that,
        otherwise if will be an html link, the method linkparser will be tried
        Headers must be passed as dictionary "header name":"header value"
        Method must be one of supported methods
        """
        # default
        self.protocol = 'http'
        self.host = linkstring
        self.url = '/'
        self.port = None
        self.setMethod(method)
        self.body = body
        self.headers = headers
        self.response = None
        self.lasterror = None
        self.errors = None

        #  Trying to parse linkstring if is a valid link http[s]://(host)[:(port)][/*]
        parsed = linkparser(linkstring)
        if (parsed is not None):
            if (_DEBUG):
                print
                parsed
            parsed = parsed[0]
            if (len(parsed) > 0 and parsed[0] is not None):
                self.protocol = parsed[0]
            if (len(parsed) > 1 and parsed[1] is not None):
                self.host = parsed[1]
            if (len(parsed) > 2 and parsed[2] is not None):
                if isinstance(parsed[2], int):
                    self.port = int(parsed[2])
                else:
                    self.url = parsed[2]
            if (len(parsed) > 3 and parsed[3] is not None):
                self.url = parsed[3]
        Thread.__init__(self, None, None,
                        self.protocol + " " + self.host + ":" + str(self.port) + " " + self.method + " " + self.url)

    def run(self):
        """Execute the method connect() spawning a new thread."""
        self.response = WebResult(None, {'status': 'Connecting', 'reason': '', 'headers': None, 'time': '-1'})
        self.response = self.connect()

    def connect(self):
        """ Try a connection using HTTP or HTTPS.
        Return a WebResult object or a list in case of errors
        """
        res = None
        startt = time.time()
        try:
            if (self.protocol == 'http'):
                h1 = h.HTTPConnection(self.host, self.port, timeout=self._HTTP_TIMEOUT)
            elif (self.protocol == 'https'):
                h1 = h.HTTPSConnection(self.host, self.port, timeout=self._HTTP_TIMEOUT)
            h1.request(self.method, self.url, self.body, self.headers)
            resp = h1.getresponse()
        except Exception as error:
            self.errors = []
            self.errors.append((str(error), self.host, self.port, self.url, self.body, self.headers))
            if (_DEBUG):
                print
                self.errors
            stopt = time.time()
            res = WebResult(self.body,
                            {'status': -1, 'reason': str(error), 'headers': self.headers, 'time': (stopt - startt)})
            self.response = None
            self.lasterror = res
            return None
        else:
            stopt = time.time()
            res = WebResult(resp.read(), {'status': resp.status, 'reason': resp.reason, 'headers': resp.getheaders(),
                                          'time': (stopt - startt)})
            if _DEBUG:
                print
                {'status': resp.status, 'reason': resp.reason, 'headers': resp.getheaders(), 'time': (stopt - startt)}
        finally:
            h1.close()
        self.response = res
        return res

    def lastError(self):
        return self.errors

    def setTimeout(self, secs=HTTP_TIMEOUT):
        """Sets up connection timeout, both for HTTP and HTTPS """
        self._HTTP_TIMEOUT = secs

    def useHTTP(self, port=h.HTTP_PORT):
        """Switch to HTTP connection, you can choose a different port """
        self.protocol = 'http'
        self.port = port

    def useHTTPS(self, port=h.HTTPS_PORT):
        """Switch to HTTPS connection, you can choose a different port """
        self.protocol = 'https'
        self.port = port

    def setHost(self, host):
        """Change hostname, must be a valid hostname only (not a link) """
        self.host = host

    def setPort(self, port=80):
        """Change up connection port """
        self.port = port

    def setMethod(self, method='GET'):
        """Change request method, must be a valid HTTP/HTTPS method (is case SENSITIVE!)"""
        if (method in _SUPPORTED_METHODS):
            self.method = method
        else:
            raise Exception(
                'Method "' + str(method) + '" not sopported\nSupported methods: ' + ", ".join(_SUPPORTED_METHODS))

    def setUrl(self, url='/'):
        """Change requested URL, must start with slash / """
        self.url = url

    def setBody(self, body=None):
        """Change body payload to send to remote host"""
        self.body = body

    def setHeaders(self, headers={}):
        """Change header to send to remote host"""
        self.headers = headers

    def __str__(self):
        st = self.protocol + "://" + self.host
        if (self.port is not None):
            st = st + ":" + str(self.port)
        st = st + "\n"
        st = st + self.method + " " + self.url + " HTTP/1.0\n"
        hs = ""
        if self.headers is not None:
            for i in self.headers:
                hs = hs + str(i) + ": " + self.headers[i] + "\n"
        st = st + hs
        st = st + "\n"
        if self.body is not None:
            st = st + self.body
        return st


class WebResult:
    """Retain result of an http connection\n\
    Data are stored as key-value with following accepted keywoards:\n
    reason,status,headers,body,time\n"""
    _ACCEPTED_KEY = ('reason', 'status', 'headers', 'body', 'time')

    def __init__(self, body, data={}):
        self.data = data
        self.data['body'] = body

    def __getitem__(self, key):
        if (key in self._ACCEPTED_KEY):
            return self.data[key]
        else:
            raise Exception('Key must be a value in: ' + ", ".join(self._ACCEPTED_KEY))

    def __setitem__(self, key, item):
        if (key in self._ACCEPTED_KEY):
            self.data[key] = item
        else:
            raise Exception('Key must be a value in: ' + ", ".join(self._ACCEPTED_KEY))

    def __delitem__(self, key):
        if (key in self._ACCEPTED_KEY):
            del (self.data[key])
        else:
            raise Exception('Key must be a value in: ' + ", ".join(self._ACCEPTED_KEY))

    def __len__(self):
        return len(self.data['body'])

    def __contains__(self, key):
        if (self.data[key] is not None):
            return True
        return False

    def __str__(self):
        st = str(self.data['status']) + " " + str(self.data['reason']) + "\n"
        hs = ""
        if self.data['headers'] is not None:
            for i in (self.data['headers']):
                hs = hs + ": ".join(i) + "\n"
        st = st + hs
        st = st + "\n"
        if self.data['body'] is not None:
            st = st + self.data['body']
        return st

    def to_list(self):
        """ Return this object as a list """
        res = []
        res.append(self.data['status'])
        res.append(self.data['reason'])
        res.append(self.data['headers'])
        res.append(self.data['body'])
        res.append(self.data['time'])
        return res

    def body(self):
        """ Return only the body """
        return str(self.data['body'])

    def headers(self):
        """ Return only the headers """
        return str(self.data['headers'])

    def status(self):
        """ Return status code and reason """
        return str(self.data['status']), str(self.data['reason'])

    def time(self):
        """ Return only the elapsed time """
        return self.data['time']

    def search(self, string, key='body'):
        """Search for the regexp 'string' into key data, key must be 'headers' or 'body'\n\
        If searched in 'body' result will be a list of matches\n\
        If searched in 'headers' result will be the value of the header(s) whose name match the regexp\n\
        """
        if (key not in ('body', 'headers')):
            raise Exception('Invalid supplied key, must be "headers" or "body" ')

        result = []
        if (key == 'body'):
            match = re.findall(str(string), str(self.data['body']))
            if (len(match) > 0):
                result = match
            else:
                result = None
        elif (key == 'headers'):
            for i in self.data['headers']:
                match = re.findall(str(string), str(i[0]))
                if (len(match) > 0):
                    result.append(str(i[1]))
        return result


class WebThread:
    """Manage multiple connection using Threads"""

    def __init__(self):
        self.childs = []
        self.arglist = []

    def __str__(self):
        k = 0
        res = ""
        for i in self.childs:
            res = res + str(k) + " " + i.name + " -> " + str(i.response['status']) + " " + i.response['reason'] + " [" + \
                  i.response['time'] + " secs]\n"
            k = k + 1
        return res

    def __len__(self):
        return len(self.childs)

    def reset(self):
        """Reset arglist"""
        del (self.arglist)
        self.arglist = []

    def spawn(self, argt=()):
        if (len(argt) == 0):
            argt = self.arglist
            t = None
        for i in argt:
            if (isinstance(i, (list, tuple)) == False):
                t = Web(i)
            else:
                if (len(i) == 2):
                    t = child(i[0], i[1])
                if (len(i) == 3):
                    t = child(i[0], i[1], i[2])
                if (len(i) == 4):
                    t = child(i[0], i[1], i[2], i[3])
            if (t != None):
                t.start()
            self.childs.append(t)
        if (_DEBUG):
            print
            "Started ", len(threading.enumerate()) - 1, " child/s"
        return len(threading.enumerate()) - 1

    def wait(self):
        """ Wait for every spawned childs to complete """
        for i in self.childs:
            i.join()

    def status(self):
        """Print a list of current child status """
        k = 0
        for i in self.childs:
            try:
                print
                k, " ", i.name, " -> ", i.response['status'], " ", i.response['reason'], " [", i.response[
                    'time'], " secs]"
            except Exception as error:
                print
                str(error)

            k = k + 1

    def info(self, n):
        """Return a list containg info about specified of None if not found"""
        k = 0
        for i in self.childs:
            if (n == k):
                return (k, " ", i.name, i.response['status'], i.response['reason'], i.response['time'])
            k = k + 1
        return None

    def data(self, n):
        """Return list representation of WebResult object of selected thread or None if not found """
        k = 0
        for i in self.childs:
            if (n == k):
                return [i.name, i.response.to_list()]
            k = k + 1
        return None

    def response(self, n):
        """Return the connection response for specified child as WebResult object."""
        k = 0
        for i in self.childs:
            if (n == k):
                return i.response
            k = k + 1
        return None

    def add(self, argt):
        """Add passed argument list to gloal list of threads to start"""
        self.arglist.append(argt)


###############################################################################

def linkparser(linkstring):
    """This function parse a string tring to seperate differents information like
    protocol(http/https), hostname, port and URI
    Returns a list of tuple in success or None otherwise
    """
    # what is this shit :)
    #    _TRIED_RE=('(http)://(.*):([0-9]*)(/.*)', '(http)://(.*):([0-9]*)', '(http)://(.*)(/.*)$', '(http)://(.*)$', '(https)://(.*):([0-9]*)(/.*)', '(https)://(.*):([0-9]*)', '(https)://(.*)(/.*)', '(https)://(.*)')
    _TRIED_RE = ('(https*)://([0-9a-z0-9A-Z\.\-_]*):*([0-9]*)(/.*$)', '')
    for restr in _TRIED_RE:
        parsed = re.findall(restr, linkstring)
        if (len(parsed) != 0):
            break

    if (len(parsed) == 0):
        return None
        raise Exception('Error while parsing link: "' + linkstring + '"')

    return parsed


def humanSize(bytes):
    if (bytes < 1):
        return "??? bytes"
    if (bytes > 1024 * 1024):
        return str(float(float(bytes) / 1024 / 1024)) + " MB"
    else:
        return str(float(float(bytes) / float(1024))) + " KB"


def humanSpeed(bytes):
    if (bytes < 1):
        return "??? bps"
    if (bytes > 1024 * 1024):
        return str(float(bytes / 1024 / 1024)) + " Mbps"
    else:
        return str(float(bytes / 1024)) + " Kbps"


def myProgressBar(count, blockSize, totalSize):
    global OLDTIME, OLDSIZE, OTIME
    if not count:
        return
    if totalSize < 0:
        totalSize = 100
    if ((time.time() - OTIME) > 0.5):
        percent = int(count * blockSize * 100 / totalSize)
        size = (count * blockSize)
        if (percent > 98 or size > totalSize):
            # sys.stdout.write("\rSaving to "+WEB_REM_FILE_NAME+"  ......100%% [] (%s / %s)          " % (humanSize(totalSize),humanSize(totalSize) ))
            sys.stdout.write("\r......100%% [] (%s / %s)          " % (humanSize(totalSize), humanSize(totalSize)))
            return
        rate = (size - OLDSIZE) / (time.time() - OLDTIME)
        OLDSIZE = size
        OLDTIME = time.time()
        # sys.stdout.write("\rSaving to "+WEB_REM_FILE_NAME+"  ......%d%% [%s] (%s / %s)          " % (percent, humanSpeed(rate),humanSize(totalSize),humanSize(size) ))
        sys.stdout.write("\r......%d%% [%s] (%s / %s)          " % (
        percent, humanSpeed(rate), humanSize(totalSize), humanSize(size)))
        sys.stdout.flush()
        OTIME = time.time()


def download(url, fname, headers={}, reporthook=None, output=False):
    global WEB_REM_FILE_NAME, OLDTIME, OLDSIZE, OTIME
    WEB_REM_FILE_NAME = fname
    OLDSIZE = 0
    OLDTIME = time.time() + 1
    OTIME = time.time()
    if (output):
        sys.stdout.write("Downloading " + url + "\n")
    try:
        urllib.urlretrieve(url, fname, reporthook)
    except Exception as error:
        print
        "ERROR: ", error
    # except KeyboardInterrupt as ki:
    # print " Download interrupted by user"
    finally:
        pass
        if (output):
            sys.stdout.write("\rDone.\n")
            sys.stdout.flush()

