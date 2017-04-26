import os
import opie
import click
import shutil
from urllib.parse import urlparse
from shutil import copytree, ignore_patterns
from os import path
from helpers import u, op1, backups
import tarfile
import requests
from requests.auth import HTTPBasicAuth

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

    click.echo("done! copied %d files, and skipped %d unchanged files." % (len(copies), skipped))


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

def get_user():
    config = u.get_config()
    if not 'auth' in config: return None
    return config['auth']['username']

def get_pass():
    config = u.get_config()
    if not 'auth' in config: return None
    return config['auth']['password']

@click.command()
@click.argument('input', type=click.Path(exists=True))
@click.option('--name', '-n', prompt=True)
@click.option('--description', '-d', prompt=True)
def upload(input, name, description):
    username = get_user()
    if username is None:
        username = click.prompt("username", type=str)
        password = click.prompt("password", type=str, hide_input=True)
        config = u.get_config()
        if not 'auth' in config: config['auth'] = {}
        config['auth']['username'] = username
        config['auth']['password'] = password
        u.write_config(config)
    else:
        password = get_pass()
    url = 'http://localhost:5000/upload'
    files = [('file', open(input, 'rb'))]
    auth = HTTPBasicAuth(username, password)
    metadata = {
        'name': name,
        'description': description,
    }

    r = requests.post(url, files=files, data=metadata, auth=auth, allow_redirects=False)
    click.echo(r.status_code)
    click.echo(r.headers['Location'])

@click.command()
@click.argument('url')
def download(url):
    click.echo("downloading {}".format(url))
    fname = path.basename(urlparse(url).path)
    fullpath = path.join(EXPORT_PATH, fname)
    if path.exists(fullpath):
        click.echo("already downloaded!")
    else:
        r = requests.get(url)
        with open(fullpath, 'wb') as f:
            f.write(r.content)

        click.echo("saved to {}".format(fullpath))
    imp(fullpath)

def imp(file):
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
@click.argument("file")
def add(file):
    imp(file)

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
cli.add_command(upload)
cli.add_command(download)

