---
author: Daniel Mohr
date: 2025-03-27
license: GPL-3.0-or-later
home: https://gitlab.com/yaml2script/yaml2script
mirror: https://github.com/yaml2script/yaml2script
documentation: https://yaml2script.gitlab.io/yaml2script/
latest_release: https://gitlab.com/yaml2script/yaml2script/-/releases/permalink/latest
doi: https://doi.org/10.5281/zenodo.14962489
---

# yaml2script

`yaml2script` is a [Python](https://www.python.org/) script that
extracts shell scripts from a
[GitLab CI/CD configuration](https://docs.gitlab.com/development/cicd/)
file `.gitlab-ci.yml` and allows you to test/analyze them with tools like
[shellcheck](https://www.shellcheck.net/).

It correctly handles [YAML anchors](https://docs.gitlab.com/ci/yaml/yaml_optimization/#yaml-anchors-for-scripts)
and [GitLab CI's 'extends'](https://docs.gitlab.com/ci/yaml/#extends)
functionality,
allowing for seamless extraction of scripts from complex '.gitlab-ci.yml'
files.

Note: The support for the
[`!reference` custom YAML tag](https://docs.gitlab.com/ci/yaml/yaml_optimization/#reference-tags)
is limited.
Specifically, references that span across files are not resolved.
In such cases, it is recommended to manually analyze each file individually.

see: [yaml2script’s documentation](https://yaml2script.gitlab.io/yaml2script/)

## Why is yaml2script useful?

* **Automated testing**:
  With yaml2script, you can automatically test your CI/CD scripts and
  ensure they are working as expected and correctly.
* **Security audits**:
  By using tools like shellcheck, yaml2script can help identify and
  fix security vulnerabilities in your scripts.
* **Code quality**:
  yaml2script can also be used to improve the code quality of your scripts
  by analyzing them with tools like pycodestyle and pylint.
* **Complex scripts**:
  If you have complex scripts in your .gitlab-ci.yml file,
  yaml2script can help extract and test them to ensure they are working
  correctly.
* **Integration with CI/CD pipelines**:
  yaml2script can be integrated directly into your CI/CD pipeline to
  automate testing and analysis, for example via
  [pre-commit](https://pre-commit.com/).

## installation

`yaml2script` requires Python 3 and the package [pyyaml](https://pyyaml.org/).
You can install it by your operating system's package management system.
Or you can have it installed automatically as a dependency of pip.

You can install `yaml2script` by running the following command:

```sh
pipx install git+https://gitlab.com/yaml2script/yaml2script.git
```

Furthermore, you will probably need a tool for checking your code such as
[shellcheck](https://www.shellcheck.net/),
[pycodestyle](https://pycodestyle.pycqa.org/en/latest/),
[pylint](https://github.com/pylint-dev/pylint)
or others.
You can also install some or all of these as optional dependency(ies):

```sh
pip3 install ".[shellcheck, pycodestyle, pylint]"
```

As far as I know you can not install these optional dependencies with `pipx`.
But you can inject them manually, e. g.:

```sh
pipx install git+https://gitlab.com/yaml2script/yaml2script.git
pipx inject yaml2script shellcheck-py pycodestyle pylint
```

If you use all dependencies from your operating system's package management
system here is an example for [Alpine Linux](https://alpinelinux.org/) using
[pycodestyle](https://pycodestyle.pycqa.org/en/latest/):

```sh
apk add --no-cache py3-pip py3-yaml py3-pycodestyle
pipx install --system-site-packages \
  git+https://gitlab.com/yaml2script/yaml2script.git
```

Or:

```sh
apk add --no-cache py3-pip py3-yaml py3-pycodestyle
pip3 install --no-deps \
  https://gitlab.com/yaml2script/yaml2script/-/archive/0.1.4/yaml2script-0.1.4.zip
```

You can also use other Linux derivatives, e. g. for
[debian](https://www.debian.org/) you could do:

```sh
apt-get install git npm pre-commit pycodestyle python3-pip python3-pytest \
  python3-pytest-cov python3-pytest-xdist python3-yaml shellcheck
pipx install --system-site-packages \
  git+https://gitlab.com/yaml2script/yaml2script.git
```

## Usage

`yaml2script` has several sub-commands:

* `extract`: Extracts scripts from the specified `.gitlab-ci.yml` file
             and prints them to stdout.
* `check`: Checks scripts from the specified `.gitlab-ci.yml` file
           using a tool like `shellcheck`.
* `all`: Checks all scripts from the specified `.gitlab-ci.yml` file
         using a tool like `shellcheck`.

Please see the help output or
[yaml2script’s documentation: command line script](https://yaml2script.gitlab.io/yaml2script/script_yaml2script.html).

### Examples

Here are some examples of how to use `yaml2script`:

Extract the specific job `foo` from a `.gitlab-ci.yml` file as a shell script:

```sh
yaml2script extract .gitlab-ci.yml foo
```

If you do not use the default name `.gitlab-ci.yml` of the
CI/CD configuration file you can adapt the line and choose your
configuration file name.

#### Examples using `shellcheck` to check the script

Check the job/script `foo` from a `.gitlab-ci.yml` file using `shellcheck`:

```sh
yaml2script check .gitlab-ci.yml foo
```

Check all jobs/scripts from a `.gitlab-ci.yml` file using `shellcheck`:

```sh
yaml2script all .gitlab-ci.yml
```

You can ignore a specific error by adding parameters for the check coommand,
e. g.:

```sh
yaml2script all .gitlab-ci.yml -parameter_check_command "-e SC2034"
```

#### Examples using `pycodestyle` to check the script

You can also do the check with another tool. For example to extract the Python
job/script `my_python-job` and check it with
[pycodestyle](https://pycodestyle.pycqa.org/en/latest/):

```sh
yaml2script check -shebang "#/usr/bin/env python" \
  -check_command pycodestyle \
  .gitlab-ci.yml my_python-job
```

#### Examples using `yaml2script` via `pre-commit`

In addition you can use it via [pre-commit](https://pre-commit.com/).

For this you need a configuration `.pre-commit-config.yaml`, which at least
defines the installation of your check tool
(e.g. [shellcheck](https://www.shellcheck.net/) installed by
[shellcheck-py](https://github.com/shellcheck-py/shellcheck-py)).

```yaml
repos:
  - repo: https://gitlab.com/yaml2script/yaml2script
    rev: latest
    hooks:
      - id: yaml2script-all
        additional_dependencies:
          - shellcheck-py
```

To ensure a repeatable experience, as described in
[Using the latest version for a repository](https://pre-commit.com/#using-the-latest-version-for-a-repository),
please replace `rev: latest` with the version you intend to use.
The value latest is only a placeholder in this README and
can not be used directly (not existing).

With this configuration, for example, the following YAML file would be tested
for errors.

```yaml
.display_env:
  before_script:
    - cat /etc/os-release

pre-commit:
  image:
    name: alpine:latest
  extends: .display_env
  script:
    - apk add --no-cache git npm pre-commit
    - pre-commit run --all-files
```

Sometimes it may make sense to add additional parameters, e. g. the following
pre-commit configuration would skip `SC1091`:

```yaml
repos:
  - repo: https://gitlab.com/yaml2script/yaml2script
    rev: latest
    hooks:
      - id: yaml2script-all
        additional_dependencies:
          - shellcheck-py
        args: [-parameter_check_command=-e SC1091]
```

To check only a specific job with
[pycodestyle](https://pycodestyle.pycqa.org/en/latest/) you could do something
like:

```yaml
repos:
  - repo: https://gitlab.com/yaml2script/yaml2script
    rev: latest
    hooks:
      - id: yaml2script-check
        additional_dependencies:
          - pycodestyle
        args: [-shebang='#!/usr/bin/env python', -check_command='pycodestyle',
               '.gitlab-ci.yml', 'my_python-job']
```

With the previous configuration, for example, the following python job could
be extracted and tested by `pycodestyle`.

```yaml
.prepare-python-env: &prepare-python-env
    - import pydoc
    - import re

my_python-job:
  image:
    name: python:latest
  script:
    - *prepare-python-env
    - print(pydoc.render_doc(re.findall))
```

If you check different jobs with different tools it could make sense to
overwrite the default `name` of the hook, e. g.:

```yaml
repos:
  - repo: https://gitlab.com/yaml2script/yaml2script
    rev: latest
    hooks:
      - id: yaml2script-check
        name: yaml2script check 'my_python-job' with pycodestyle
        additional_dependencies:
          - pycodestyle
        args: [-shebang='', -check_command='pycodestyle',
               '.gitlab-ci.yml', 'my_python-job']
```

#### Examples using `yaml2script` in a CI pipeline

Or you can run `yaml2script` in a CI pipeline:

```yaml
shellcheck_.gitlab-ci.yml:
  stage: pre
  image:
    name: alpine:latest
  script:
    - apk add --no-cache py3-pip py3-yaml shellcheck
    - pip3 install --no-deps --break-system-packages .
    - yaml2script all .gitlab-ci.yml
```

## copyright + license

Author: Daniel Mohr.

Date: 2025-03-27

License: GNU General Public License Version 3 or any later version(GPLv3+)

Copyright (C) 2024-2025 Daniel Mohr

This tool was derived from
[yaml2script.py](https://gitlab.com/deploy2zenodo/deploy2zenodo/-/blob/3c9b1eb502ace2fe0cf045e7c6632a2eb4b97bb5/yaml2script.py)
which was part of [deploy2zenodo](https://doi.org/10.5281/zenodo.10112959).
