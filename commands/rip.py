import os
import sys
import time
import opie
import click
import tarfile
import usb.core
import usb.util
from datetime import datetime
from helpers import op1, rips

@click.command()
@click.option('--name', '-n', prompt=True)
def cli(name):
    rips.assert_environment()

    mount = op1.get_mount_or_die_trying()
    print("Found at %s" % mount)

    rips.create_rip(mount, name)
