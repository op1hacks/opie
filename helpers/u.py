import os
import hashlib

HOME = os.path.join(os.getenv("HOME"), ".opie")

def get_visible_folders(d):
    return list(filter(lambda x: os.path.isdir(os.path.join(d, x)), get_visible_children(d)))

def get_visible_children(d):
    return list(filter(lambda x: x[0] != '.', os.listdir(d)))

def get_file_checksum(path):
    return hashlib.sha256(open(path, 'rb').read()).digest()

