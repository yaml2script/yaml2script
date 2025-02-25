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
    - CREATED_SCRIPTS=$(mktemp -d)
    - |
      JOBNAMES="$(mktemp)"
      grep -E "^([^ ]+):$" < .gitlab-ci.yml | sed 's/://' > "$JOBNAMES"
      while IFS= read -r jobname
      do
        ./yaml2script .gitlab-ci.yml "$jobname" | \
          tee "$CREATED_SCRIPTS/$jobname"
      done < "$JOBNAMES"
      rm "$JOBNAMES"
    - shellcheck -e SC1091 "$CREATED_SCRIPTS"/*
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
    - CREATED_SCRIPTS=$(mktemp -d)
    - |
      JOBNAMES="$(mktemp)"
      grep -E "^([^ ]+):$" < .gitlab-ci.yml | sed 's/://' > "$JOBNAMES"
      while IFS= read -r jobname
      do
        ./yaml2script .gitlab-ci.yml "$jobname" | \
          tee "$CREATED_SCRIPTS/$jobname"
      done < "$JOBNAMES"
      rm "$JOBNAMES"
    - shellcheck -e SC1091 "$CREATED_SCRIPTS"/*
```
