#!/usr/bin/env python

import argparse
import os
from   pathlib import Path
import subprocess

parser = argparse.ArgumentParser(description="sort ROMS by type")
parser.add_argument('--path', required=True)

args = parser.parse_args()

root_path       = Path(os.path.abspath(args.path))
unlicensed_path = root_path / 'unlicensed'
unlicensed_tags = ['(unl)']
beta_path       = root_path / 'beta'
beta_tags       = ['(proto)', ('beta')]
imported_path   = root_path / 'imported'
native_tags     = ['USA', 'World']
zip_path        = root_path / 'zip'

os.makedirs(str(unlicensed_path), exist_ok=True)
os.makedirs(str(beta_path),       exist_ok=True)
os.makedirs(str(imported_path),   exist_ok=True)
os.makedirs(str(zip_path),        exist_ok=True)

files = os.listdir(args.path)
files = [i for i in files if os.path.isfile(str(root_path / i))]

def file_has(filename, tags):
    for tag in tags:
        if tag.lower() in filename.lower():
            return True
    return False

def move_to(filename, path):
    source = str(root_path / filename)
    dest   = str(path / filename)
    os.rename(source, dest)

for i in files:
    if file_has(i, unlicensed_tags):
        move_to(i, unlicensed_path)
    elif file_has(i, beta_tags):
        move_to(i, beta_path)
    elif not file_has(i, native_tags):
        move_to(i, imported_path)
    else:
        subprocess.run(['unzip', str(root_path / i), '-d', str(root_path)])
        move_to(i, zip_path)
