#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  mangacli2.py
#  1.2
#
#  Copyright (c) 2014 -  Manuel Bovo  <manuel.bovo@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

import sys
import os
import logging
import ConfigParser
import threading
import Queue

import lib.web as web

__version__ = '120'
__doc__ = "Version 1.2 by Manuel Bovo\n\
    This is the main MangaDownloader application\
    \n\
    1.0.0: First version\
    1.2.0: Current multithreaded version\n"


class MangaDownloader:
    log = None

    _multithread = False
    _module = None
    _dryrun = 0
    _output_dir = None
    _output_format = None
    _temp_dir = None
    _cleanup = False

    _manga_name = None
    _manga_sequential = False
    _manga_from = 0
    _manga_to = 0
    _manga_uselist = False
    _manga_list = []
    _manga_subset = False

    def __init__(self, configfile):

        self.log = logging.getLogger('MangaDownloader')  # from parent configuration ;)

        self.log.info("Loading configuration file [" + configfile + ']')
        try:
            config = ConfigParser.ConfigParser()
            config.readfp(open(configfile))
            _v = config.getint('MANGADOWNLOADER', 'version')
            if (_v != int(__version__)):
                print
                "WARNING: Invalid version!!"
            self._multithread = config.getboolean('MANGADOWNLOADER', 'multithread')
            self._module = config.get('MANGADOWNLOADER', 'module')
            self._dryrun = config.getboolean('MANGADOWNLOADER', 'dryrun')
            self._output_dir = config.get('MANGADOWNLOADER', 'output_dir')
            self._output_format = config.get('MANGADOWNLOADER', 'output_format')
            self._temp_dir = config.get('MANGADOWNLOADER', 'temp_dir')
            self._cleanup = config.getboolean('MANGADOWNLOADER', 'cleanup')

            self._manga_name = config.get('MANGA', 'name')
            self._manga_sequential = config.getboolean('MANGA', 'sequential')
            self._manga_from = config.getint('MANGA', 'from')
            self._manga_to = config.getint('MANGA', 'to')
            self._manga_uselist = config.getboolean('MANGA', 'uselist')

            l = config.get('MANGA', 'list')
            for i in l.split(','):
                self._manga_list.append(int(i))

            self._manga_subset = config.getboolean('MANGA', 'subset')

            self.log.debug("\tMultithread :\t" + str(self._multithread))
            self.log.debug("\tModule      :\t" + str(self._module))
            self.log.debug("\tDryrun      :\t" + str(self._dryrun))
            self.log.debug("\tOutput dir  :\t" + str(self._output_dir))
            self.log.debug("\tOutput fmt  :\t" + str(self._output_format))
            self.log.debug("\tTemp dir    :\t" + str(self._temp_dir))
            self.log.debug("\tCleanup     :\t" + str(self._cleanup))
            self.log.debug("")
            self.log.debug("\tManga name  :\t" + str(self._manga_name))
            self.log.debug("\tSubset      :\t" + str(self._manga_subset))
            self.log.debug("\tSequential  :\t" + str(self._manga_sequential))
            self.log.debug("\tFrom        :\t" + str(self._manga_from))
            self.log.debug("\tTo          :\t" + str(self._manga_to))
            self.log.debug("\tUse list    :\t" + str(self._manga_uselist))
            self.log.debug("\tList        :\t" + str(self._manga_list))

            longname = "import modules." + self._module + " as child"
            exec(longname)
            self.log.info("Loaded [" + child.__name__ + "] from [" + child.__file__ + "]")
            self.child = child

        except Exception as error:
            self.log.error(str(error))
            raise error

    def start(self):
        # try:

        tdh = None  # the downloader thread use after
        cpageList = self.child.SafeList()
        self.cnameList = self.child.SafeList()
        cow = self.child.Crawler(self._manga_name, name='Crawler', args=(cpageList, self.cnameList))

        self.log.info("Running the crawler")
        cow.start()
        cow.join()
        biglist = cpageList.list()
        todolist = []
        self.log.info("Crawler returns " + str(len(biglist)) + " chapters links")
        if (self._manga_subset):
            self.log.info("Get a subset of")
            if (self._manga_sequential):
                todolist = biglist[(self._manga_from - 1):self._manga_to]
                self.log.info("\tSequential subset[" + str(self._manga_from) + ":" + str(self._manga_to) + "]: " + str(
                    len(todolist)) + " elements")
            else:
                self.log.debug("\t'sequential' is false")
            if (self._manga_uselist):
                self.log.info("\tMerging with user defined list -> " + str(self._manga_list))
                for elem in self._manga_list:
                    try:
                        todolist.append(biglist[elem])
                    except IndexError as ie:
                        self.log.warning('\tListed element [' + str(elem) + '] not found by crawler, ignoring')
                        continue
            else:
                self.log.debug("\t'uselist' is false")
        else:
            todolist = biglist
        print
        biglist
        self.log.info("Added " + str(len(todolist)) + " chapters")
        allpages = dict()
        allthreads = dict()
        self.humanmap = dict()
        n = 0
        for chapter in todolist:
            p = self.child.SafeList()

            t = threading.Thread(name='Chapter ' + str(n + 1), target=cow.getPageList, args=(chapter, p))
            t.start()
            # self.log.debug("\t"+str(t.ident))

            allthreads[t.ident] = t
            allpages[t.ident] = p
            self.humanmap[t.ident] = n + 1  # map the id -> chapter num
            n = n + 1

        # waitin for threads, when a thread finish start the getImage
        self.allimages = dict()
        subthreads = dict()
        download_started = False
        while True:
            main_thread = threading.currentThread()
            n = 0
            for key, t in allthreads.items():
                if (not t.isAlive()):
                    allpages[key].ready()
                    self.log.info("Starting buildImageList for " + t.name)

                    # ok setup for image list retrieving
                    imglist = self.child.SafeList()
                    self.allimages[key] = imglist
                    k = 0
                    plist = allpages[t.ident]
                    sublist = []
                    for page in plist.list():
                        st = threading.Thread(name=t.name + " Page " + str(k), target=cow.buildImageList,
                                              args=(page, k, imglist))
                        st.start()
                        sublist.append(st)
                        k = k + 1
                    subthreads[key] = sublist  # saving the list of all subthreads
                    allthreads.pop(t.ident, None)
                    # self.log.debug("\tStarted "+str(k)+" subthreads")
                    if (self._multithread):
                        tdh = threading.Thread(name=t.name, target=self.downloader, args=(imglist, key))
                        tdh.start()
                n = n + 1

            # check them
            for key, tlist in subthreads.items():
                count = 0
                for t in tlist:
                    if (not t.isAlive()): count = count + 1
                if (count == len(tlist)):  # all dead man!
                    self.allimages[key].ready()  # mark this list ready!

            if (len(threading.enumerate()) == 1): break
            pass

        n = 0
        for key, pagelist in allpages.items():

            self.log.info("Chapter " + str(self.humanmap[key]) + ": " + str(len(pagelist.list())) + " pages, " + str(
                len(self.allimages[key].list())) + " images")
            # print self.allimages[key].list()
            if (not self._multithread):
                self.downloader(self.allimages[key].list(), key)
            n = n + 1

    def downloader(self, imglist=None, key=0, ):

        self.log.info("Waiting for image list " + str(key))
        imglist.waitfor()  # wait for completion

        if self._dryrun:
            self.log.warning("Dryrun is true, skipping download phase")

        if not self._dryrun:
            try:
                os.mkdir(self._output_dir)
            except Exception as error:
                self.log.warning("mkdir [" + self._output_dir + "] fail:  " + str(error))

            try:
                os.mkdir(self._output_dir + "/" + self._manga_name)
            except Exception as error:
                self.log.warning("mkdir [" + self._output_dir + "/" + self._manga_name + "] fail:  " + str(error))

        cn = ""
        if self.humanmap[key] < 100:
            cn = "0"
        if self.humanmap[key] < 10:
            cn = cn + "0"
        cn = cn + str(self.humanmap[key])

        chapdir = self._output_format.replace('%m', self._manga_name).replace('%n', cn).replace('%t',
                                                                                                self.cnameList.list()[
                                                                                                    self.humanmap[
                                                                                                        key]].replace(
                                                                                                    ' ', '_'))

        if not self._dryrun:
            try:
                os.mkdir(self._output_dir + "/" + self._manga_name + "/" + chapdir)
            except Exception as error:
                self.log.warning(
                    "mkdir [" + self._output_dir + "/" + self._manga_name + "/" + chapdir + "] fail:  " + str(error))

        for record in imglist.list():
            page = record[0]
            url = record[1]

            fn = ""
            if page < 100:
                fn = "0"
            if page < 10:
                fn = fn + "0"
            fn = fn + str(page)

            fname = self._output_dir + "/" + self._manga_name + "/" + chapdir + "/" + fn + ".jpg"
            self.log.debug("Get " + url + "  ==> " + fname)

            if not self._dryrun:
                nth = threading.Thread(name="C " + str(cn) + "P " + str(fn), target=web.download,
                                       args=(url, fname, {}, None, False))
                nth.start()

            # web.download(url,fname,reporthook=None,output=False)


if __name__ == '__main__':
    print
    "-------------------------------------------------------------"
    print
    "         Hallo! This is MangaDownloader v", __version__
    print
    ""
    print
    "!! Please invoke it in the right way:                      !!"
    print
    "!! Use cli.py for Command line interface                   !!"
    print
    "!! Use gui.py for Graphical User Interface                 !!"
    print
    "-------------------------------------------------------------"
    quit(-1)
else:
    pass
