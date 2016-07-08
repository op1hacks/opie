import os
import opie
import click
import shutil
from shutil import copytree, ignore_patterns
from os import path
from helpers import u, op1, backups
import tarfile

PACK_PATH = path.join(u.HOME, "packs")
EXPORT_PATH = path.join(u.HOME, "pkg")

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
@click.option('--group', '-g', default='opie', prompt=True)
@click.option('--type', '-t', type=click.Choice(['drum', 'synth']), prompt=True)
def push(group, type):
    mount = op1.get_mount_or_die_trying()
    (copies, skipped) = u.dirtydiff(path.join(PACK_PATH, type), group, path.join(mount, type))

    if len(copies) > 0:
        with click.progressbar(copies) as tasks:
            for task in tasks:
                os.makedirs(path.split(task[1])[0], exist_ok=True)
                shutil.copy2(task[0], task[1])

    click.echo("done! skipped %d unchanged files." % (skipped))

@click.command()
@click.option('--group', '-g', default='opie', prompt=True)
@click.option('--type', '-t', type=click.Choice(['drum', 'synth']), prompt=True)
@click.option('--output-dir', '-o', default=EXPORT_PATH, prompt=True)
def export(group, type, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    name = path.join(output_dir, "{}.tar.xz".format(group))
    source = path.join(PACK_PATH, type, group)
    with tarfile.open(name, "x:xz") as tar:
        tar.add(source, path.join(type, group), exclude=lambda x: x[0] == '.')
    click.echo("exported as %s" % name)

@click.command()
@click.argument("file")
def add(file):
    if not path.exists(file):
        click.echo("File doesn't exist.")

    with tarfile.open(file, "r:xz") as tar:
        members = [x for x in tar.getmembers()
                   if (x.isdir() and path.split(x.name[:-1])[0] in ['drum','synth'])
                   or x.name[-4:] == '.aif']

        tar.extractall(PACK_PATH, members)
        for member in members:
            click.echo(member.name)

        click.echo("\ndone!")

@click.command()
def list():
    synths = os.listdir(path.join(PACK_PATH, "synth"))
    drums = os.listdir(path.join(PACK_PATH, "drum"))
    click.echo("SYNTH")
    for synth in synths:
        if not synth[0] == '.':
            click.echo("  %s" % synth)
    click.echo("DRUM")
    for drum in drums:
        if not drum[0] == '.':
            click.echo("  %s" % drum)

cli.add_command(make)
cli.add_command(sync)
cli.add_command(push)
cli.add_command(export)
cli.add_command(add)
cli.add_command(list)

