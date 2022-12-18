import os
import sys
import time
import opie
import click
import tarfile
import usb.core
import usb.util
from helpers import u
from datetime import datetime

BACKUPS_DIR = os.path.join(u.HOME, "backups")
ARCHIVE_FORMAT = "opie-backup-%Y-%m-%d-%H%M%S.tar.xz"

def assert_environment():
    os.makedirs(BACKUPS_DIR, exist_ok=True)

def generate_archive(mount, save_dir):
    name = os.path.join(save_dir, datetime.now().strftime(ARCHIVE_FORMAT))
    print("writing backup as %s" % (name))
    with tarfile.open(name, "x:xz") as tar:
        with click.progressbar(u.get_visible_children(mount)) as children:
            for child in children:
                tar.add(os.path.join(mount, child), child, exclude=lambda x: x[0] == '.')
    print("backup created.")

def restore_archive(file, mount):
    with tarfile.open(file, "r:xz") as tar:
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(tar, path=mount)
    print("successfully restored from archive.")

