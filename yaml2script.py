#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# SPDX-FileCopyrightText: 2024-2025 Daniel Mohr
#    yaml2script.py
#    Copyright (C) 2024-2025  Daniel Mohr
#    Version: 0.1.2
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
    - apk add --no-cache py3-yaml shellcheck
    - CREATED_SCRIPTS=$(mktemp -d)
    - |
      JOBNAMES="$(mktemp)"
      grep -E "^([^ ]+):$" < .gitlab-ci.yml | sed 's/://' > "$JOBNAMES"
      while IFS= read -r jobname
      do
        ./yaml2script.py .gitlab-ci.yml "$jobname" | \
          tee "$CREATED_SCRIPTS/$jobname"
      done < "$JOBNAMES"
      rm "$JOBNAMES"
    - shellcheck -e SC1091 "$CREATED_SCRIPTS"/*

Or directly with the inline script (has to be created):

shellcheck_.gitlab-ci.yml:
  stage: pre
  image:
    name: alpine:latest
  script:
    - apk add --no-cache py3-yaml shellcheck
    - |
      #!/usr/bin/env python3
      # SPDX-License-Identifier: BSD-3-Clause
      # SPDX-FileCopyrightText: 2024-2025 Daniel Mohr
      ...
    - ...

This could also be created as GitLab CI-Template.
"""

import sys
import warnings

import yaml


def main():
    """
    Extracts scripts from the specified '.gitlab-ci.yml' file and
    prints them to stdout.

    It correctly handles YAML anchors and GitLab CI's 'extends' functionality,
    allowing for seamless extraction of scripts from complex '.gitlab-ci.yml'
    files.
    """
    if len(sys.argv) != 3:
        print('yaml2script [filename] [job name]')
        sys.exit(1)
    with open(sys.argv[1], encoding='utf8') as fd:
        data = yaml.load(fd, Loader=yaml.SafeLoader)
    script = {}
    if 'extends' in data[sys.argv[2]]:
        for key in ['before_script', 'script', 'after_script']:
            if data[sys.argv[2]]['extends'] in data:
                if key in data[data[sys.argv[2]]['extends']]:
                    script[key] = data[data[sys.argv[2]]['extends']][key]
            else:
                warnings.warn('job to extend not available: ignoring')
    for key in ['before_script', 'script', 'after_script']:
        if key in data[sys.argv[2]]:
            script[key] = data[sys.argv[2]][key]
    script_code = ['#!/usr/bin/env sh']
    for key in ['before_script', 'script', 'after_script']:
        if key in script:
            script_code += script[key]
    print('\n'.join(script_code))


if __name__ == "__main__":
    main()
