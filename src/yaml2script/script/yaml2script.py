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
import os
import subprocess
import sys
import tempfile
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
    return sys.exit(0)


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
    return sys.exit(0)


def run_check_script(args):
    """
    :Author: Daniel Mohr
    :Date: 2025-02-25
    :License: GPL-3.0
    """
    # args.filename[0]
    # args.jobname
    # args.check_command[0]
    # args.parameter_check_command
    commoncmd = args.check_command[0]
    commoncmd += " " + ' '.join(args.parameter_check_command)
    returncode = 0
    with tempfile.TemporaryDirectory() as tmpdir:
        for jobname in args.jobname:
            if args.verbose:
                print('extract', jobname, 'from', args.filename[0])
            script_code = '\n'.join(extract_script(args.filename[0], jobname))
            scriptfilename = os.path.join(tmpdir, jobname)
            with open(scriptfilename, 'w', encoding='utf8') as fd:
                fd.write(script_code)
            cmd = commoncmd + " " + scriptfilename
            if args.verbose:
                print('run', cmd)
            cpi = subprocess.run(
                cmd,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir, check=False)
            returncode += cpi.returncode
            if not args.quiet:
                if cpi.stdout.decode():
                    print(cpi.stdout.decode())
                if cpi.stderr.decode():
                    print(cpi.stderr.decode())
            if args.verbose:
                print('returncode', cpi.returncode)
    if args.verbose:
        print('returncode sum', returncode)
    return returncode


def main():
    """
    Extracts scripts from the specified '.gitlab-ci.yml' file and
    prints them to stdout.

    It correctly handles YAML anchors and GitLab CI's 'extends' functionality,
    allowing for seamless extraction of scripts from complex '.gitlab-ci.yml'
    files.
    """
    preepilog = "Examples:\n\n"
    preepilog += "yaml2script extract .gitlab-ci.yml pre-commit\n\n"
    preepilog += "yaml2script check .gitlab-ci.yml pre-commit pycodestyle\n\n"
    postepilog = "Author: Daniel Mohr\n"
    postepilog += "yaml2script Version: "
    postepilog += importlib.metadata.version(
        __package__.split('.', maxsplit=1)[0]) + "\n"
    postepilog += "License: GPL-3.0"
    postepilog += "\n\n"
    epilog = preepilog + postepilog
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
    # subparser check scripts
    preepilog = "Example:\n\n"
    preepilog += "yaml2script check .gitlab-ci.yml pre-commit pycodestyle\n\n"
    epilog = preepilog + postepilog
    parser_check_script = subparsers.add_parser(
        'check',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help='For more help: yaml2script check -h',
        description='Check scripts from the specified ".gitlab-ci.yml" '
        'file.',
        epilog=epilog)
    parser_check_script.set_defaults(func=run_check_script)
    parser_check_script.add_argument(
        'filename',
        nargs=1,
        type=str,
        help='From this filename the script(s) will be extracted.')
    parser_check_script.add_argument(
        'jobname',
        nargs="+",
        type=str,
        help='These jobname(s) will be extracted and checked.')
    parser_check_script.add_argument(
        '-check_command',
        nargs=1,
        type=str,
        required=False,
        default=["shellcheck"],
        dest='check_command',
        help='Use this tool to check script(s). default: shellcheck')
    parser_check_script.add_argument(
        '-parameter_check_command',
        nargs="+",
        type=str,
        required=False,
        default=["-e SC1091"],
        dest='parameter_check_command',
        help='Parameter for the check command. default: "-e SC1091"')
    parser_check_script.add_argument(
        '-quiet',
        default=False,
        required=False,
        action='store_true',
        dest='quiet',
        help='No output from check command.')
    parser_check_script.add_argument(
        '-verbose',
        default=False,
        required=False,
        action='store_true',
        dest='verbose',
        help='verbose output')
    # parse arguments
    args = parser.parse_args()
    if args.subparser_name is not None:
        sys.exit(args.func(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
