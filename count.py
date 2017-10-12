#!/usr/bin/env python

import argparse
import os
from   pathlib import Path
import subprocess

parser = argparse.ArgumentParser(description="sort ROMS by type")
parser.add_argument('--path', required=True)

args = parser.parse_args()

root_path       = Path(os.path.abspath(args.path))


files = os.listdir(args.path)
files = [i for i in files if os.path.isfile(str(root_path / i))]

games = 0
for i in files:
    games += 1

system = root_path.name
print('You have {0} {1} games'.format(games, system))
