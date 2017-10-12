#!/usr/bin/env python

import argparse
import os
from   pathlib import Path
import subprocess

import lib

parser = argparse.ArgumentParser(description="sort ROMS by type")
parser.add_argument('--path', required=True)

args = parser.parse_args()

root_path       = Path(os.path.abspath(args.path))

if root_path.is_file():
    lib.fix_header(str(root_path))
else:
    lib.fix_headers(root_path)
