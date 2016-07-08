import os
import opie
import click
import shutil
import subprocess
from subprocess import run
from helpers import u, op1, backups

@click.command()
def cli():
    if not op1.is_connected():
        exit("OP-1 doesn't appear to be connected.")
    mount = op1.find_op1_mount()
    if mount is None:
        exit("Looks like your best friend already dismounted.")

    click.echo(run(["diskutil", "unmount", mount], stderr=subprocess.STDOUT).stdout)
