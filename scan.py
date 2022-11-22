#!/usr/bin/python3

import os
import datetime
import sys

import mp3
import flac


SUPPORTED_FORMATS = ["mp3", "flac"]

class ScanCollection(object):
    ''' 
    Scan a given path and enter/update the metadata in the database
    '''

    def __init__(self, music_dir):
        self.music_dir = music_dir
        self.collection = []
        self.skipped = 0
        self.total = 0

    def get_collection(self):
        return self.collection

    def scan(self):
        self.traverse("")

    def traverse(self, relative_path):

        if not relative_path:
            fullpath = self.music_dir
        else:
            fullpath = os.path.join(self.music_dir, relative_path)

        for f in os.listdir(fullpath):
            if f in ['.', '..']: 
                continue

            new_relative_path = os.path.join(relative_path, f)
            new_full_path = os.path.join(self.music_dir, new_relative_path)
            if os.path.isfile(new_full_path): 
                self.add(new_relative_path)
            if os.path.isdir(new_full_path): 
                if not self.traverse(new_relative_path):
                    return False

        return True

    def add(self, relative_path):

        fullpath = os.path.join(self.music_dir, relative_path)
        self.total += 1

        # Check to see if the file in question has changed since the last time
        # we looked at it. If not, skip it for speed
        stats = os.stat(fullpath)
        ts = datetime.datetime.fromtimestamp(stats[8])

        base, ext = os.path.splitext(relative_path)
        ext = ext.lower()[1:]
        base = os.path.basename(relative_path)
        if ext not in SUPPORTED_FORMATS:
#            print("ignore %s" % base)
            self.skipped += 1
            return

        if ext == "mp3":
            mdata = mp3.read(os.path.join(self.music_dir, relative_path))
        elif ext == "flac":
            mdata = flac.read(os.path.join(self.music_dir, relative_path))
#        print("   add %-31s %-31s" % (mdata["recording"][:30], mdata["artist"][:30]))

        mdata["file_name"] = fullpath

        self.collection.append(mdata)
