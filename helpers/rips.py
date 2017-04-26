import os
import sys
import time
import opie
import click
import shutil
import tarfile
import usb.core
import usb.util
from helpers import u
from datetime import datetime
from os import path
from subprocess import check_call

RIPS_DIR = os.path.join(u.HOME, "rips")

def assert_environment():
    os.makedirs(RIPS_DIR, exist_ok=True)

def transcode(input, codec, output, codec_flags=[]):
    binary = "ffmpeg"
    if shutil.which("ffmpeg") == None:
        if shutil.which("avconv") == None:
            click.echo("ffmpeg is required!")
            return
        else:
            binary = "avconv"

    base = [binary, "-loglevel", "warning","-stats"]
    args = base + \
        ["-i", input] + \
        ["-c:a", codec] + \
        codec_flags + \
        [output]
    click.echo(args)
    check_call(args)

def create_rip(mount, name):
    fullpath = path.join(RIPS_DIR, name)
    albums = path.join(mount, "album")
    sides = ["side_a", "side_b"]

    os.makedirs(fullpath, exist_ok=False)
    click.echo("writing rips to %s" % (fullpath))

    # initial transcode to lossless format
    for side in sides:
        click.echo("transcoding " + side)
        transcode(path.join(albums, side+".aif"), "flac", path.join(fullpath, side+".flac"))
    click.echo("ripped to lossless formats, now transcoding to some convenience formats.")
    for side in sides:
        origin = path.join(fullpath, side+".flac")
        click.echo("transcoding %s to alac".format(side))
        transcode(origin, "alac", path.join(fullpath, side+".m4a"))
        click.echo("transcoding %s to mp3 v0".format(side))
        transcode(origin, "libmp3lame", path.join(fullpath, side+".mp3"), ["-q:a", "0"])

    click.echo("ripped!")
