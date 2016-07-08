import os
import opie
import click
from helpers import u, op1, backups

@click.command()
def cli():
    backups.assert_environment()

    click.echo("backups found in " + backups.BACKUPS_DIR)
    archives = u.get_visible_children(backups.BACKUPS_DIR)
    i = 0
    for archive in archives:
        click.echo("%d. %s" % (i, archive))
        i += 1

    choice = click.prompt('Choose a backup', type=int)

    if choice < 0 or choice >= len(archives):
        exit("Invalid selection.")

    click.echo("you went with %d huh?" % (choice))

    mount = op1.get_mount_or_die_trying()
    print("Found at %s" % mount)

    click.echo("Restoring %s to %s" % (archives[choice], backups.BACKUPS_DIR))
    backups.restore_archive(os.path.join(backups.BACKUPS_DIR, archives[choice]), mount)

