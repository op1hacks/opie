import os
import sys
import time
import opie
import click
import tarfile
import usb.core
import usb.util
from datetime import datetime
from helpers import backups

@click.command(cls=opie.OpieCLI)
def cli():
    backups.assert_environment()

    if not backups.is_connected():
        print("Please connect your OP-1 and put it in DISK mode (Shift+COM -> 3)...")
        backups.wait_for_connection()

    print("OP-1 detected!")

    mount = backups.find_op1_mount()
    if mount is None:
        print("Waiting for OP-1 disk to mount...")
        mount = backups.wait_for_op1_mount()
        if mount is None:
            exit("Failed to find mount point of OP-1. Feel free to file an issue.")
    print("Found at %s" % mount)

    backups.generate_archive(mount, backups.BACKUPS_DIR)
