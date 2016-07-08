import os
import hashlib
from os import path

HOME = os.path.join(os.getenv("HOME"), ".opie")

def get_visible_folders(d):
    return list(filter(lambda x: os.path.isdir(os.path.join(d, x)), get_visible_children(d)))

def get_visible_children(d):
    return list(filter(lambda x: x[0] != '.', os.listdir(d)))

def get_file_checksum(path):
    return hashlib.sha256(open(path, 'rb').read()).digest()

def dirtydiff(mount, source, target):
    skipped = 0
    copies = []
    for root, dirs, files in os.walk(os.path.join(mount, source), topdown=True):
        if "user" in dirs:
            del dirs[dirs.index("user")]
        for file in files:
            src = path.join(root, file)
            dst = path.join(target, path.relpath(src, mount))
            if not path.exists(dst) or get_file_checksum(src) != get_file_checksum(dst):
                copies.append((src, dst))
            else:
                skipped += 1
    return (copies, skipped)
