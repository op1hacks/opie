import os
import opie
import click
import shutil
from helpers import u, op1, backups

def get_preset_path(mount, type, preset):
    return os.path.join(mount, type, "user", "%d.aif"%(preset))

@click.group()
def cli():
    pass

@click.command()
@click.option('--name', '-n', prompt=True)
@click.option('--group', '-g', default='opie', prompt=True)
@click.option('--type', '-t', type=click.Choice(['drum', 'synth']), prompt=True)
@click.option('--preset', '-p', type=click.IntRange(1, 8), prompt=True)
def make(name, group, type, preset):
    mount = op1.get_mount_or_die_trying()
    source = get_preset_path(mount, type, preset)
    dest_dir = os.path.join(mount, type, group)
    os.makedirs(dest_dir, exist_ok=True)

    dest = os.path.join(dest_dir, "%s.aif"%(name))
    if (os.path.exists(dest)):
        exit("that name is already taken in the group! be more creative!")

    shutil.copy(source, dest)
    click.echo("%s created!" % (dest))

cli.add_command(make)
