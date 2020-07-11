#!/usr/bin/env python3
#-*-encoding:utf-8*-

from core import launch_hsh
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    # Subparser for aliases
    #   save -> Command save, alias on the project directory
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    launch_hsh(args)
