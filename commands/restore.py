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
# @click.option('file', help="The direct path of an archive to restore.", default=None)
def cli():
    backups.assert_environment()

    archives = backups.get_visible_children(backups.BACKUPS_DIR)
    i = 0
    for archive in archives:
        click.echo("%d. %s" % (i, archive))
        i += 1

    choice = click.prompt('Choose a backup', type=int)

    if choice < 0 or choice >= len(archives):
        exit("Invalid selection.")

    click.echo("you went with %d huh?" % (choice))
    if not backups.is_connected():
        print("Please connect your OP-1 and put it in DISK mode (Shift+COM -> 3)...")
        wait_for_connection()

    print("OP-1 detected!")

    mount = backups.find_op1_mount()
    if mount is None:
        print("Waiting for OP-1 disk to mount...")
        mount = backups.wait_for_op1_mount()
        if mount is None:
            exit("Failed to find mount point of OP-1. Feel free to file an issue.")

    print("Found at %s" % mount)

    click.echo("Restoring %s to %s" % (archives[choice], backups.BACKUPS_DIR))
    backups.restore_archive(os.path.join(backups.BACKUPS_DIR, archives[choice]), mount)

