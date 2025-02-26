# yaml2script

`yaml2script` is a [Python](https://www.python.org/) script that
extracts shell scripts from a
[GitLab CI/CD configuration](https://docs.gitlab.com/17.5/development/cicd/)
file `.gitlab-ci.yml` and allows you to test/analyze them with tools like
[shellcheck](https://www.shellcheck.net/).

## installation

`yaml2script` requires Python 3 and the package [pyyaml](https://pyyaml.org/).
You can install it by your operating system's package management system.
Or you can have it installed automatically as a dependency of pip.

You can install `yaml2script` by running the following command:

```sh
pip3 install .
```

Furthermore, you will probably need your tool for checking your code such as
[shellcheck](https://www.shellcheck.net/),
[pycodestyle](https://pycodestyle.pycqa.org/en/latest/),
[pylint](https://github.com/pylint-dev/pylint)
or others.
You can also install some or all of these as optional dependency(ies):

```sh
pip3 install ".[shellcheck, pycodestyle, pylint]"
```

If you use all dependencies from your operating system's package management
system here is an example for [Alpine Linux](https://alpinelinux.org/) using
[pycodestyle](https://pycodestyle.pycqa.org/en/latest/):

```sh
apk add --no-cache py3-pip py3-yaml py3-pycodestyle
pip3 install --no-deps .
```

## Usage

`yaml2script` has several sub-commands:

* `extract`: Extracts scripts from the specified `.gitlab-ci.yml` file
             and prints them to stdout.
* `check`: Checks scripts from the specified `.gitlab-ci.yml` file
           using a tool like `shellcheck`.
* `all`: Checks all scripts from the specified `.gitlab-ci.yml` file
         using a tool like `shellcheck`.

Please see the help output.

#### Examples

Here are some examples of how to use `yaml2script`:

Extract the specific job `foo` from a `.gitlab-ci.yml` file as a shell script:

```sh
yaml2script extract .gitlab-ci.yml foo
```

If you do not use the default name of the CI/CD configuration file
you can adapt the line and choose your configuration file.

Check the job/script `foo` from a `.gitlab-ci.yml` file using `shellcheck`:

```sh
yaml2script check .gitlab-ci.yml foo
```

Check all jobs/scripts from a `.gitlab-ci.yml` file using `shellcheck`:

```sh
yaml2script all .gitlab-ci.yml
```

You can also do the check with another tool. For example to extract the Python
job/script `my_python-job` and check it with
[pycodestyle](https://pycodestyle.pycqa.org/en/latest/):

```sh
yaml2script check -check_command pycodestyle -parameter_check_command "" .gitlab-ci.yml my_python-job
```

In addition you can use it via [pre-commit](https://pre-commit.com/).

Therefore you need a config `.pre-commit-config.yaml` defining at least your
check tool (e. g. [shellcheck](https://www.shellcheck.net/) installed via
[shellcheck-py](https://github.com/shellcheck-py/shellcheck-py)):

```yaml
repos:
  - repo: to be done
    rev: latest
    hooks:
      - id: yaml2script-all
        additional_dependencies:
          - shellcheck-py
```

Too check only a specific job with
[pycodestyle](https://pycodestyle.pycqa.org/en/latest/) you could do something
like:

```yaml
repos:
  - repo: to be done
    rev: latest
    hooks:
      - id: yaml2script-check
        additional_dependencies:
          - pycodestyle
	args: [-check_command='pycodestyle', -parameter_check_command='', '.gitlab-ci.yml', 'my_python-job']
```

Or you can run `yaml2script` it in a CI pipeline:

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

Date: 2025-02-26

License: GPL-3.0

Copyright (C) 2024-2025 Daniel Mohr

This tool was derived from
[yaml2script.py](https://gitlab.com/deploy2zenodo/deploy2zenodo/-/blob/3c9b1eb502ace2fe0cf045e7c6632a2eb4b97bb5/yaml2script.py)
which was part of [deploy2zenodo](https://doi.org/10.5281/zenodo.10112959).
