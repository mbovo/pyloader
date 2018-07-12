#!/usr/bin/env python2
##
## app.py
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

__version__ = '1.0'
__doc__ = "Version 1.0.0 by Manuel Bovo\n\
\
"

_CONFIG_SECTION_DEFAULT = "Default"
_CONFIG_SECTION_NETWORK = "Network"
_CONFIG_SECTION_MANGA = "Manga"
_CONFIG_SECTION_DOWNLOADER = "Downloader"
_CONFIG_SECTION_ENGINE = "Engine"

from Tkinter import *
import ttk
import tkMessageBox
import ConfigParser
import thread
# my libs
import tools, web


class App(Frame):
    _configured = False

    def __init__(self, master=None):

        Frame.__init__(self, master)

        self._WEBHOST = StringVar()
        self._MANGA = StringVar()
        self._V = StringVar()
        self._VI = IntVar()
        self._OUTDIR = StringVar()
        self._DRYRUN = BooleanVar()
        self._CLEANUP = BooleanVar()
        self._TEMPDIR = StringVar()

        self.grid()

        self.main = Frame(self)

        self.ct1 = Frame(self.main)
        self.ct1_lb1 = Label(self.ct1, text="Config file: ")
        self.entry_confname = Entry(self.ct1)
        self.entry_confname.insert(0, "./default.conf")
        self.bt_load = Button(self.ct1, text="Load", fg="green", command=self.loadconf)

        self.ct1_lb1.pack(side=LEFT)
        self.bt_load.pack(side=BOTTOM)
        self.entry_confname.pack(side=RIGHT)

        self.ct2 = Frame(self.main)

        ct2_ct1 = Frame(self.ct2)
        self.ct2_lb1 = Label(ct2_ct1, text="Host: ")
        self.ct2_lb1.pack(side=LEFT)
        self.ct2_en1 = Entry(ct2_ct1, state=DISABLED, width=30, disabledforeground="black", textvariable=self._WEBHOST)
        self.ct2_en1.pack()
        ct2_ct1.pack()

        ct2_ct2 = Frame(self.ct2)
        self.ct2_lb2 = Label(ct2_ct2, text="Manga: ")
        self.ct2_lb2.pack(side=LEFT)
        self.ct2_en2 = Entry(ct2_ct2, state=DISABLED, width=30, disabledforeground="black", textvariable=self._MANGA)
        self.ct2_en2.pack()
        ct2_ct2.pack()

        ct2_ct3 = Frame(self.ct2)
        self.ct2_lb3 = Label(ct2_ct3, text="Volume List: ")
        self.ct2_lb3.pack(side=LEFT)
        self.ct2_en3 = Entry(ct2_ct3, state=DISABLED, width=30, disabledforeground="black", textvariable=self._V)
        self.ct2_en3.pack()
        ct2_ct3.pack()

        ct2_ct3 = Frame(self.ct2)
        self.ct2_lb3 = Label(ct2_ct3, text="Volumes (count): ")
        self.ct2_lb3.pack(side=LEFT)
        self.ct2_en3 = Entry(ct2_ct3, state=DISABLED, width=30, disabledforeground="black", textvariable=self._VI)
        self.ct2_en3.pack()
        ct2_ct3.pack()

        ct2_ct4 = Frame(self.ct2)
        self.ct2_lb4 = Label(ct2_ct4, text="Output: ")
        self.ct2_lb4.pack(side=LEFT)
        self.ct2_en4 = Entry(ct2_ct4, state=DISABLED, width=30, disabledforeground="black", textvariable=self._OUTDIR)
        self.ct2_en4.pack()
        ct2_ct4.pack()

        ct2_ct5 = Frame(self.ct2)
        self.ct2_lb5 = Label(ct2_ct5, text="DRYRUN: ")
        self.ct2_lb5.pack(side=LEFT)
        self.ct2_en5 = Entry(ct2_ct5, state=DISABLED, width=30, disabledforeground="black", textvariable=self._DRYRUN)
        self.ct2_en5.pack()
        ct2_ct5.pack()

        ct2_ct6 = Frame(self.ct2)
        self.ct2_lb6 = Label(ct2_ct6, text="CLEANUP: ")
        self.ct2_lb6.pack(side=LEFT)
        self.ct2_en6 = Entry(ct2_ct6, state=DISABLED, width=30, disabledforeground="black", textvariable=self._CLEANUP)
        self.ct2_en6.pack()
        ct2_ct6.pack()

        ct2_ct7 = Frame(self.ct2)
        self.ct2_lb7 = Label(ct2_ct7, text="TEMPDIR: ")
        self.ct2_lb7.pack(side=LEFT)
        self.ct2_en7 = Entry(ct2_ct7, state=DISABLED, width=30, disabledforeground="black", textvariable=self._TEMPDIR)
        self.ct2_en7.pack()
        ct2_ct7.pack()

        self.ct1.pack(side=LEFT)
        self.ct2.pack(side=RIGHT)
        self.main.pack(side=TOP)

        self.entry_confname.focus_set()

        self.bottom = Frame(self)
        self.btgo = Button(self.bottom, text="Run", command=self.go)
        self.btgo.pack(side=LEFT)
        self.btquit = Button(self.bottom, text="Quit", fg="red", command=self.quit)
        self.btquit.pack(side=RIGHT)
        self.bottom.pack()

    def go(self):
        if (self._configured == False):
            tkMessageBox.showerror("Invalid Configuration", "Please load a configuratio file first")
        else:
            self.real_go()

    def real_go(self):

        self.dwnframe = Frame(self)
        self.dwnframe.pack()

        sw = SideView(self.dwnframe)
        # sw.title ("Downloading processes")

        thread.start_new_thread(tools.getPages, (
        self._WEBHOST.get(), self._MANGA.get(), self._VOL, self._OUTDIR.get(), self._DRYRUN.get(), self._CLEANUP.get(),
        self._TEMPDIR.get(), self.PBAR, self.LOCALSTATUS, self.GLOBALSTATUS, sw))
        # tools.getPages(self._WEBHOST.get(), self._MANGA.get(),self._VOL,self._OUTDIR.get(),self._DRYRUN.get(),self._CLEANUP.get(),self.PBAR,self.LOCALSTATUS,self.GLOBALSTATUS)

    def quitme(self):
        self.quit()

    def loadconf(self):
        try:
            config = ConfigParser.ConfigParser()
            config.readfp(open(self.entry_confname.get()))
            config.read

            self._WEBHOST.set(config.get(_CONFIG_SECTION_NETWORK, 'host'))
            self._MANGA.set(config.get(_CONFIG_SECTION_MANGA, 'manganame'))
            self._V.set(config.get(_CONFIG_SECTION_MANGA, 'volumes'))
            self._OUTDIR.set(config.get(_CONFIG_SECTION_DOWNLOADER, 'output'))
            self._DRYRUN.set(config.getboolean(_CONFIG_SECTION_DOWNLOADER, 'dryrun'))
            self._CLEANUP.set(config.getboolean(_CONFIG_SECTION_ENGINE, 'cleanup_temp'))
            self._TEMPDIR.set(config.get(_CONFIG_SECTION_ENGINE, 'temp_dir'))

            self._configured = True

            self._VOL = []
            s = self._V.get()
            e = 0
            for i in s.split(','):
                self._VOL.append(int(i))
                e = e + 1
            self._VI.set(e)
            self.PBAR = IntVar()
            self.LOCALSTATUS = StringVar()
            self.GLOBALSTATUS = StringVar()
            self.barcont = Frame(self)

            self.GLOBALSTATUS.set("Ready")

            self.globalstatus = Label(self.barcont, text="Status", textvariable=self.GLOBALSTATUS)
            self.globalstatus.pack(side=LEFT)
            self.globalbar = ttk.Progressbar(self.barcont, length=400, maximum=e, variable=self.PBAR)
            self.globalbar.pack(side=RIGHT)

            self.barcont2 = Frame(self)
            self.localstatus = Label(self.barcont2, text="Status2", width=50, textvariable=self.LOCALSTATUS)
            self.localstatus.pack(side=BOTTOM)

            self.barcont.pack()
            self.barcont2.pack()

        except Exception as error:
            print
            "-- ERROR: loading configuration file failed"
            print
            "         ", error
            tkMessageBox.showerror("Load Configuration", "%s" % str(error))


class SideView(Frame):

    def __init__(self, master=None):
        # Toplevel.__init__(self,master)
        Frame.__init__(self, master)

        self.grid()
        self.main = Frame(self)
        self.lbl = Label(self.main, text="List of download threads")
        self.lbl.pack()
        self.main.pack()

    def addBar(self, maxval, variable, status):
        tframe = Frame(self)
        tlabel = Label(tframe, width=50, textvariable=status)
        tbar = ttk.Progressbar(tframe, length=250, maximum=maxval, variable=variable)
        tlabel.pack(side=LEFT)
        tbar.pack(side=RIGHT)
        tframe.pack()
        return tframe

    def delBar(self, h):
        h.pack_forget();


def run():
    app = App()
    app.master.title('Manga Downloader')
    app.mainloop()
    try:
        app.destroy()
    except Exception as e:
        exit(0)
