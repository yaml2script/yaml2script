# yaml2script

Usage example 1:

```yaml
shellcheck_.gitlab-ci.yml:
  stage: pre
  image:
    name: alpine:latest
  script:
    - apk add --no-cache pipx
    - pipx install .
    - yaml2script all .gitlab-ci.yml
```

Usage example 2:

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

Via pre-commit:

```yaml
repos:
  - repo: to be done
    rev: ?
    hooks:
      - id: yaml2script
        additional_dependencies:
	  - shellcheck-py
```

If you changed the name of the CI/CD configuration file:

```yaml
repos:
  - repo: to be done
    rev: ?
    hooks:
      - id: yaml2script
        additional_dependencies:
	  - shellcheck-py
        files: my_gitlab_ci.yaml
```

Via pre-commit using pycodestyle:

```yaml
repos:
  - repo: to be done
    rev: ?
    hooks:
      - id: yaml2script
        additional_dependencies:
	  - pycodestyle
        files: ''
	types: [python]
	args: [-parameter_check_command='']
```
