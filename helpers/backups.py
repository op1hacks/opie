import os
import sys
import time
import opie
import click
import tarfile
import usb.core
import usb.util
from datetime import datetime

VENDOR_TE = 0x2367
PRODUCT_OP1 = 0x0002
OP1_BASE_DIRS = set(['tape', 'album', 'synth', 'drum'])
BACKUPS_DIR = os.path.join(os.getenv("HOME"), ".opie", "backups")
ARCHIVE_FORMAT = "opie-backup-%Y-%m-%d-%H%M%S.tar.xz"

def is_connected():
    return usb.core.find(idVendor=VENDOR_TE, idProduct=PRODUCT_OP1) is not None

def wait_for_connection():
    try:
        while True:
            time.sleep(1)
            if is_connected():
                break
    except KeyboardInterrupt:
        sys.exit(0)

def assert_environment():
    if sys.platform != "darwin":
        sys.exit("Currently only OS X is supported. Pull requests are accepted ;)")
    os.makedirs(BACKUPS_DIR, exist_ok=True)

def get_visible_folders(d):
    return list(filter(lambda x: os.path.isdir(os.path.join(d, x)), get_visible_children(d)))

def get_visible_children(d):
    return list(filter(lambda x: x[0] != '.', os.listdir(d)))

def find_op1_mount(root="/Volumes"):
    dirs = get_visible_folders(root)

    for dir in dirs:
        subdirs = get_visible_folders(os.path.join(root, dir))
        if set(subdirs) & OP1_BASE_DIRS == OP1_BASE_DIRS:
            return os.path.join(root, dir)
    return None

def wait_for_op1_mount(timeout=5, root="/Volumes"):
    i=0
    try:
        while i < timeout:
            time.sleep(1)
            mount = find_op1_mount(root)
            if mount is not None:
                return mount
            i += 1
    except KeyboardInterrupt:
        sys.exit(0)

def generate_archive(mount, save_dir):
    name = os.path.join(save_dir, datetime.now().strftime(ARCHIVE_FORMAT))
    with tarfile.open(name, "x:xz") as tar:
        with click.progressbar(get_visible_children(mount)) as children:
            for child in children:
                tar.add(os.path.join(mount, child), child, exclude=lambda x: x[0] == '.')
    print("created %s" % (name))

def restore_archive(file, mount):
    with tarfile.open(file, "r:xz") as tar:
        tar.extractall(path=mount)
    print("successfully restored from archive.")

