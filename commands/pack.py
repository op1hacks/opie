import os
import opie
import click
import shutil
from shutil import copytree, ignore_patterns
from os import path
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

@click.command()
def sync():
    mount = op1.get_mount_or_die_trying()
    target = os.path.join(u.HOME, "packs")

    skipped = 0
    copies = []
    for source in ["synth", "drum"]:
        for root, dirs, files in os.walk(os.path.join(mount, source), topdown=True):
            if "user" in dirs:
                del dirs[dirs.index("user")]
            for file in files:
                src = path.join(root, file)
                dst = path.join(target, path.relpath(src, mount))
                if not path.exists(dst) or u.get_file_checksum(src) != u.get_file_checksum(dst):
                    copies.append((src, dst))
                else:
                    skipped += 1

    if len(copies) > 0:
        with click.progressbar(copies) as tasks:
            for task in tasks:
                os.makedirs(path.split(task[1])[0], exist_ok=True)
                shutil.copy2(task[0], task[1])

    click.echo("done! skipped %d files since they're unchanged." % (skipped))


@click.command()
@click.option('--type', '-t', prompt=True)
@click.option('--name', '-n', prompt=True)
@click.option('--group', '-g', prompt=True)
def push():
    click.echo("not yet implemented")


cli.add_command(make)
cli.add_command(sync)
