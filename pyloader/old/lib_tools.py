#!/usr/bin/env python2
##
## manga.py
##
## Copyright (C) 2011 - Manuel Bovo
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
##

import re, os, sys
import pickle
import thread
from Tkinter import IntVar, StringVar

import web

__version__ = '1.0'
__doc__ = "Version 1.0.0 by Manuel Bovo\n\
\
"

_DEBUG = 0

if __name__ == '__main__':
    print
    "-------------------------------------------------"
    print
    "Hallo! This is module manga ", __version__
    print
    "!! Python modules can be used with 'import' !! "
    print
    "Please for help use help(manga)"
    print
    "Have fun!"
    print
    "-------------------------------------------------"
    print
    "GNU Public Licens v3.0 -- Written by Manuel Bovo     "
    print
    "-------------------------------------------------"
    quit(-1)
else:
    pass


def getPages(_WEBHOST, _MANGA, _VOL, _OUTDIR, _DRYRUN, _CLEANUP, _TEMPDIR, _PBAR, _LOCALS, _GLOBALS, side_window):
    for vol in _VOL:

        errors = 0
        imgarray = []

        _PBAR.set(_PBAR.get() + 1)
        print
        "+++ Volume " + str(vol)
        _GLOBALS.set("Parsing Volume " + str(vol))

        # if (os.path.exists("./mangareader_"+str((vol-1))+".temp")):
        #    try:
        #        os.remove("./mangareader_"+str((vol-1))+".temp")
        #    except Exception as error:
        #        print error
        #        print "Failed to remove .temp file, please remove it by hand before try another execution!"

        if (os.path.exists(_TEMPDIR + "/" + _MANGA + "_" + str(vol) + ".temp")):
            print
            "---- .temp file found! Resuming..."
            f = open(_TEMPDIR + "/" + _MANGA + "_" + str(vol) + ".temp", "r")
            imgarray = pickle.load(f)
            f.close()
        else:
            print
            "---- Retrieving links"
            # set up multi page
            currpage = "/" + _MANGA + "/" + str(vol) + "/"
            nextpage = currpage

            numpage = 0
            sys.stdout.write("------ Pages: ")
            while (re.match(currpage, nextpage)):

                # Make the url 	eg: http://www.mangareader.net:80/super-darling/1/
                url = _WEBHOST + nextpage
                sys.stdout.write(str(numpage) + " ")
                _LOCALS.set("Page: " + str(numpage))
                sys.stdout.flush()
                numpage = numpage + 1

                # create the object and try to connect
                w = web.Web(url)
                res = w.connect()
                if (res is None and w.lasterror is not None):
                    print
                    "---- Error connecting to " + url + "  " + str(w.lasterror)
                    continue

                # Retrieve image link
                strarray = res.search("img.*" + _MANGA + ".*jpg")

                if (strarray is None):
                    sys.stdout.write("E! ")
                    errors = errors + 1
                    if (errors >= _MAXERRORS):
                        raise Exception("-- CRITICAL: Too many errors encountered. Aborted.")
                else:
                    for s in strarray:
                        image = re.split("^.*src.\"", s)
                        imgarray.append(image[1])

                # Retrieve the next page link
                if (strarray is None):
                    sys.stdout.write("E! ")
                    errors = errors + 1
                    if (errors >= _MAXERRORS):
                        raise Exception("-- CRITICAL: Too many errors encountered, Aborted.")
                else:
                    strarray = res.search(".*img.*" + _MANGA)
                    nextpage = ""
                    for s in strarray:
                        k = re.split("^.*href=\"", s)
                        k = re.split("\".*", k[1])
                        nextpage = k[0]
        # print "------ Saving temp list."
        try:
            f = open(_TEMPDIR + "/" + _MANGA + "_" + str(vol) + ".temp", "w")
            pickle.dump(imgarray, f)
            f.close()
        except Exception as error:
            print
            "-- ERROR: Saving temp file failed!"
            print
            "         ", error

        print
        "---- Found " + str(len(imgarray)) + " images."

        thread.start_new_thread(download, (side_window, vol, _OUTDIR, _DRYRUN, imgarray))

        if (_CLEANUP == True):
            try:
                os.remove(_TEMPDIR + "/" + _MANGA + "_" + str(vol) + ".temp")
            except Exception as error:
                print
                "-- ERROR: Failed to cleanup .temp files, please remove it by hand before try another execution!"
                print
                "        ", error
        else:
            print
            "++ Keeping temp files in place"


def download(sw, vol, _OUTDIR, _DRYRUN, imgarray=[]):
    if (_DRYRUN == False):

        try:
            idb = IntVar()
            sdb = StringVar()
            sdb.set("Volume " + str(vol) + "\t\t 0/" + str(len(imgarray)))
            h = sw.addBar(len(imgarray), idb, sdb)
        except Exception as e:
            print
            e

        # print "++++ Downloading Volume "+str(vol)
        outdir = _OUTDIR + "vol_" + str(vol) + "/"
        if (not os.path.exists(_OUTDIR)):
            try:
                print
                "mkdir " + _OUTDIR
                os.mkdir(_OUTDIR)
            except Exception as error:
                print
                error
        if (not os.path.exists(outdir)):
            try:
                print
                "mkdir " + outdir
                os.mkdir(outdir)
            except Exception as error:
                print
                error

        num = 1

        for img in imgarray:
            if num < 10:
                cnum = "00"
            elif num < 100:
                cnum = "0"
            cnum = cnum + str(num)
            web.download(img, outdir + cnum + ".jpg", None)
            idb.set(num)
            sdb.set("Volume " + str(vol) + "\t\t " + str(num) + "/" + str(len(imgarray)))
            num = num + 1

        sw.delBar(h)
    else:
        print
        "---- DRY run! Skip downloading\n"
