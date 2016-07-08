import os
import sys
import time
import opie
import click
import tarfile
import usb.core
import usb.util
from datetime import datetime
from helpers import op1, backups

@click.command()
def cli():
    backups.assert_environment()

    mount = op1.get_mount_or_die_trying()
    print("Found at %s" % mount)

    backups.generate_archive(mount, backups.BACKUPS_DIR)
