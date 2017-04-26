import os
import hashlib
import configparser
from os import path

HOME = os.path.join(os.getenv("HOME"), "opie")
CONFIG_FILE = path.join(HOME, "opie.cfg")

def get_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config

def write_config(config):
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

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
