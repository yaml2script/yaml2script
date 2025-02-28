#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2024-2025 Daniel Mohr
#
# yaml2script extracts the scripts from a '.gitlab-ci.yml' file.
# Copyright (C) 2024-2025 Daniel Mohr
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
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
    - yaml2script all .gitlab-ci.yml

:Author: Daniel Mohr
:License: GPLv3+
:Copyright: (C) 2024-2025 Daniel Mohr
"""

import argparse
import importlib
import os
import re
import subprocess
import sys
import tempfile
import warnings

import yaml


def run_version(_):
    """
    :Author: Daniel Mohr
    :Date: 2025-02-25
    :License: GPLv3+
    """
    version = importlib.metadata.version(__package__.split(".", maxsplit=1)[0])
    print(f'yaml2script version {version}')
    return sys.exit(0)


def _flatten_list(unflatten_list):
    """
    :Author: Daniel Mohr
    :Date: 2025-02-25
    :License: GPLv3+

    flatten the given list
    """
    flatten_list = []
    for item in unflatten_list:
        if isinstance(item, list):
            flatten_list.extend(_flatten_list(item))
        else:
            flatten_list.append(item)
    return flatten_list


def extract_script(filename, jobname, *, shebang='#!/usr/bin/env sh'):
    """
    :Author: Daniel Mohr
    :Date: 2025-02-27
    :License: GPLv3+

    Extracts scripts from the specified filename and returns the script.

    It correctly handles YAML anchors and GitLab CI's 'extends' functionality,
    allowing for seamless extraction of scripts from complex '.gitlab-ci.yml'
    files.
    """
    with open(filename, encoding='utf8') as fide:
        data = yaml.load(fide, Loader=yaml.SafeLoader)
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
    script_code = []
    if shebang:
        script_code += [shebang]
    for key in ['before_script', 'script', 'after_script']:
        if key in script:
            script_code += script[key]
    return list(map(str.strip, _flatten_list(script_code)))


def run_extract_script(args):
    """
    :Author: Daniel Mohr
    :Date: 2025-02-26
    :License: GPLv3+
    """
    script_code = os.linesep.join(extract_script(
        args.filename[0], args.jobname[0], shebang=args.shebang[0]))
    print(script_code)
    return sys.exit(0)


def _run_check_script(
        filename, all_jobnames, check_command, parameter_check_command, *,
        shebang='#!/usr/bin/env sh', verbose=False, quiet=False):
    """
    :Author: Daniel Mohr
    :Date: 2025-02-28
    :License: GPLv3+
    """
    # pylint: disable=too-many-arguments
    parameter_check_command = tuple(filter(None, parameter_check_command))
    if len(parameter_check_command) >= 1:
        check_command += " " + ' '.join(parameter_check_command)
    returncode = 0
    with tempfile.TemporaryDirectory() as tmpdir:
        for jobname in all_jobnames:
            if verbose:
                print('extract', jobname, 'from', filename)
            script_code = os.linesep.join(extract_script(
                filename, jobname, shebang=shebang))
            scriptfilename = os.path.join(tmpdir, jobname)
            with open(scriptfilename, 'w', encoding='utf8') as fide:
                fide.write(script_code + os.linesep)
                fide.flush()
            cmd = check_command + " " + scriptfilename
            if verbose:
                print('run', cmd)
            cpi = subprocess.run(
                cmd,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir, check=False)
            returncode += cpi.returncode
            if not quiet:
                if cpi.stdout.decode():
                    print(cpi.stdout.decode())
                if cpi.stderr.decode():
                    print(cpi.stderr.decode())
            if verbose:
                print('returncode', cpi.returncode)
    if verbose:
        print('returncode sum', returncode)
    return returncode


def run_check_script(args):
    """
    :Author: Daniel Mohr
    :Date: 2025-02-25
    :License: GPLv3+
    """
    return _run_check_script(
        args.filename[0], args.jobname, args.check_command[0],
        args.parameter_check_command,
        shebang=args.shebang[0], verbose=args.verbose, quiet=args.quiet)


def run_check_all_scripts(args):
    """
    :Author: Daniel Mohr
    :Date: 2025-02-25
    :License: GPLv3+
    """
    with open(args.filename[0], encoding='utf8') as fide:
        lines = fide.read()
    jobnames = tuple(
        map(str.strip,
            re.findall(r'^([^ ]+):$', lines, re.MULTILINE)))
    return _run_check_script(
        args.filename[0], jobnames, args.check_command[0],
        args.parameter_check_command,
        shebang=args.shebang[0], verbose=args.verbose, quiet=args.quiet)


def _my_argument_parser():
    """
    :Author: Daniel Mohr
    :Date: 2025-02-27
    :License: GPLv3+
    """
    preepilog = "Examples:" + 2 * os.linesep
    preepilog += "yaml2script extract .gitlab-ci.yml pre-commit"
    preepilog += 2 * os.linesep
    preepilog += "yaml2script check .gitlab-ci.yml pre-commit pycodestyle"
    preepilog += 2 * os.linesep
    postepilog = "Author: Daniel Mohr" + os.linesep
    postepilog += "yaml2script Version: "
    postepilog += importlib.metadata.version(
        __package__.split('.', maxsplit=1)[0]) + os.linesep
    postepilog += "License: GNU General Public License Version 3 "
    postepilog += "or any later version (GPLv3+)"
    postepilog += 2 * os.linesep
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
    parser_extract_script.add_argument(
        '-shebang',
        nargs=1,
        type=str,
        required=False,
        default=["#!/usr/bin/env sh"],
        dest='shebang',
        help='The first line of the script output. You can set it to an empty'
        'string to skip it. default: "#!/usr/bin/env sh"')
    # subparser check scripts
    preepilog = "Example:" + 2 * os.linesep
    preepilog += "yaml2script check .gitlab-ci.yml pre-commit pycodestyle"
    preepilog += 2 * os.linesep
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
        '-shebang',
        nargs=1,
        type=str,
        required=False,
        default=["#!/usr/bin/env sh"],
        dest='shebang',
        help='The first line of the script output. You can set it to an empty'
        'string to skip it. default: "#!/usr/bin/env sh"')
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
        default=[""],
        dest='parameter_check_command',
        metavar='param',
        help='Parameter for the check command. Since the script is extracted '
        'in a temporary folder, external resources may not be available. '
        'It would be sensible to inform the check command (e. g. shellcheck) '
        'about this, e. g. with "-e SC1091". Default: ""')
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
    # subparser check all scripts
    preepilog = "Example:" + 2 * os.linesep
    preepilog += "yaml2script all .gitlab-ci.yml"
    preepilog += 2 * os.linesep
    epilog = preepilog + postepilog
    parser_check_all_scripts = subparsers.add_parser(
        'all',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help='For more help: yaml2script all -h',
        description='Check all scripts from the specified ".gitlab-ci.yml" '
        'file.',
        epilog=epilog)
    parser_check_all_scripts.set_defaults(func=run_check_all_scripts)
    parser_check_all_scripts.add_argument(
        'filename',
        nargs=1,
        type=str,
        help='From this filename the script(s) will be extracted.')
    parser_check_all_scripts.add_argument(
        '-shebang',
        nargs=1,
        type=str,
        required=False,
        default=["#!/usr/bin/env sh"],
        dest='shebang',
        help='The first line of the script output. You can set it to an empty'
        'string to skip it. default: "#!/usr/bin/env sh"')
    parser_check_all_scripts.add_argument(
        '-check_command',
        nargs=1,
        type=str,
        required=False,
        default=["shellcheck"],
        dest='check_command',
        help='Use this tool to check script(s). default: shellcheck')
    parser_check_all_scripts.add_argument(
        '-parameter_check_command',
        nargs="+",
        type=str,
        required=False,
        default=[""],
        dest='parameter_check_command',
        metavar='param',
        help='Parameter for the check command. Since the script is extracted '
        'in a temporary folder, external resources may not be available. '
        'It would be sensible to inform the check command (e. g. shellcheck) '
        'about this, e. g. with "-e SC1091". Default: ""')
    parser_check_all_scripts.add_argument(
        '-quiet',
        default=False,
        required=False,
        action='store_true',
        dest='quiet',
        help='No output from check command.')
    parser_check_all_scripts.add_argument(
        '-verbose',
        default=False,
        required=False,
        action='store_true',
        dest='verbose',
        help='verbose output')
    return parser


def main():
    """
    :Author: Daniel Mohr
    :Date: 2025-02-26
    :License: GPLv3+

    Extracts scripts from the specified '.gitlab-ci.yml' file and
    prints them to stdout.

    It correctly handles YAML anchors and GitLab CI's 'extends' functionality,
    allowing for seamless extraction of scripts from complex '.gitlab-ci.yml'
    files.
    """
    parser = _my_argument_parser()
    # parse arguments
    args = parser.parse_args()
    if args.subparser_name is not None:
        sys.exit(args.func(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
