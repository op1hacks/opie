import os
import sys
import time
import opie
import click
import tarfile
import usb.core
import usb.util
from helpers import u
from datetime import datetime
from subprocess import check_call

RIPS_DIR = os.path.join(u.HOME, "rips")

def assert_environment():
    os.makedirs(RIPS_DIR, exist_ok=True)

def create_rip(mount, name):
    fullpath = os.path.join(RIPS_DIR, name)
    albums = os.path.join(mount, "album")
    os.makedirs(fullpath, exist_ok=False)
    print("writing rips to %s" % (fullpath))

    print("transcoding side_a")
    check_call(["ffmpeg", "-loglevel", "warning","-stats","-i", os.path.join(albums, "side_a.aif"),
    	 "-c:a", "alac", os.path.join(fullpath, "side_a.m4a")])

    print("transcoding side_b")
    check_call(["ffmpeg", "-loglevel", "warning","-stats","-i", os.path.join(albums, "side_b.aif"),
    	 "-c:a", "alac", os.path.join(fullpath, "side_b.m4a")])
    print("backup created.")

