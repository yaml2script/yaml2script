#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# SPDX-FileCopyrightText: 2024-2025 Daniel Mohr
#    yaml2script.py
#    Copyright (C) 2024-2025  Daniel Mohr
#    Version: 0.1.3
#    License: GPLv3
#
# This script tries to extract the scripts from a '.gitlab-ci.yml' file.
# In this way the scripts inside '.gitlab-ci.yml' can be tested/analyzed for
# example with 'shellcheck'.
"""
This script extracts the scripts from a '.gitlab-ci.yml' file.
This allows the scripts inside '.gitlab-ci.yml' to be tested/analyzed
with tools like 'shellcheck'.

You can use it in a CI pipline, e. g.:

shellcheck_.gitlab-ci.yml:
  stage: pre
  image:
    name: alpine:latest
  script:
    - apk add --no-cache py3-pip py3-yaml shellcheck
    - pip3 install --no-deps --break-system-packages .
    - CREATED_SCRIPTS=$(mktemp -d)
    - |
      JOBNAMES="$(mktemp)"
      grep -E "^([^ ]+):$" < .gitlab-ci.yml | sed 's/://' > "$JOBNAMES"
      while IFS= read -r jobname
      do
        ./yaml2script extract .gitlab-ci.yml "$jobname" | \
          tee "$CREATED_SCRIPTS/$jobname"
      done < "$JOBNAMES"
      rm "$JOBNAMES"
    - shellcheck -e SC1091 "$CREATED_SCRIPTS"/*
"""

import argparse
import importlib
import sys
import warnings

import yaml


def run_version(_):
    """
    :Author: Daniel Mohr
    :Date: 2025-02-25
    :License: GPL-3.0
    """
    version = importlib.metadata.version(__package__.split(".", maxsplit=1)[0])
    print(f'yaml2script version {version}')


def extract_script(filename, jobname):
    """
    :Author: Daniel Mohr
    :Date: 2025-02-25
    :License: GPL-3.0

    Extracts scripts from the specified filename and returns the script.

    It correctly handles YAML anchors and GitLab CI's 'extends' functionality,
    allowing for seamless extraction of scripts from complex '.gitlab-ci.yml'
    files.
    """
    with open(filename, encoding='utf8') as fd:
        data = yaml.load(fd, Loader=yaml.SafeLoader)
    script = {}
    if 'extends' in data[jobname]:
        for key in ['before_script', 'script', 'after_script']:
            if data[jobname]['extends'] in data:
                if key in data[data[jobname]['extends']]:
                    script[key] = data[data[jobname]['extends']][key]
            else:
                warnings.warn('job to extend not available: ignoring')
    for key in ['before_script', 'script', 'after_script']:
        if key in data[jobname]:
            script[key] = data[jobname][key]
    script_code = ['#!/usr/bin/env sh']
    for key in ['before_script', 'script', 'after_script']:
        if key in script:
            script_code += script[key]
    return script_code


def run_extract_script(args):
    """
    :Author: Daniel Mohr
    :Date: 2025-02-25
    :License: GPL-3.0
    """
    script_code = extract_script(args.filename[0], args.jobname[0])
    print('\n'.join(script_code))


def main():
    """
    Extracts scripts from the specified '.gitlab-ci.yml' file and
    prints them to stdout.

    It correctly handles YAML anchors and GitLab CI's 'extends' functionality,
    allowing for seamless extraction of scripts from complex '.gitlab-ci.yml'
    files.
    """
    epilog = "Example:\n\n"
    epilog += "yaml2script .gitlab-ci.yml pre-commit\n\n"
    epilog += "Author: Daniel Mohr\n"
    epilog += "yaml2script Version: "
    epilog += importlib.metadata.version(
        __package__.split('.', maxsplit=1)[0]) + "\n"
    epilog += "License: GPL-3.0"
    epilog += "\n\n"
    parser = argparse.ArgumentParser(
        description='yaml2script extracts the scripts '
        'from a .gitlab-ci.yml file.',
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    # subparsers
    subparsers = parser.add_subparsers(
        dest='subparser_name',
        help='There are different sub-commands with there own flags.')
    # subparser version
    parser_version = subparsers.add_parser(
        'version',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help='return version of detloclcheck',
        description='display version information of detloclcheck',
        epilog=epilog)
    parser_version.set_defaults(func=run_version)
    # subparser extract_script
    parser_extract_script = subparsers.add_parser(
        'extract',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help='For more help: yaml2script extract -h',
        description='Extracts scripts from the specified ".gitlab-ci.yml" '
        'file and prints them to stdout.',
        epilog=epilog)
    parser_extract_script.set_defaults(func=run_extract_script)
    parser_extract_script.add_argument(
        'filename',
        nargs=1,
        type=str,
        help='From this filename the script will be extracted.')
    parser_extract_script.add_argument(
        'jobname',
        nargs=1,
        type=str,
        help='This jobname will be extracted.')
    args = parser.parse_args()
    if args.subparser_name is not None:
        sys.exit(args.func(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
