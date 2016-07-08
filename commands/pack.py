import os
import opie
import click
import shutil
from shutil import copytree, ignore_patterns
from os import path
from helpers import u, op1, backups

PACK_PATH = path.join(u.HOME, "packs")

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

@click.command()
def sync():
    mount = op1.get_mount_or_die_trying()

    copies = []
    skipped = 0
    for source in ["synth", "drum"]:
        (copy, skip) = u.dirtydiff(mount, source, PACK_PATH)
        copies += copy
        skipped += skip

    if len(copies) > 0:
        with click.progressbar(copies) as tasks:
            for task in tasks:
                os.makedirs(path.split(task[1])[0], exist_ok=True)
                shutil.copy2(task[0], task[1])

    click.echo("done! skipped %d unchanged files." % (skipped))


@click.command()
@click.option('--type', '-t', prompt=True)
@click.option('--group', '-g', prompt=True)
def push(type, group):
    mount = op1.get_mount_or_die_trying()
    (copies, skipped) = u.dirtydiff(path.join(PACK_PATH, type), group, path.join(mount, type))

    if len(copies) > 0:
        with click.progressbar(copies) as tasks:
            for task in tasks:
                os.makedirs(path.split(task[1])[0], exist_ok=True)
                shutil.copy2(task[0], task[1])

    click.echo("done! skipped %d unchanged files." % (skipped))


cli.add_command(make)
cli.add_command(sync)
cli.add_command(push)

