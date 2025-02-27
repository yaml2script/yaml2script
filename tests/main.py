"""
:Author: Daniel Mohr
:Email: daniel.mohr@uni-greifswald.de
:Date: 2025-02-27
:License: GPL-3.0-or-later

aggregation of tests

You can run this file directly::

  env python3 main.py
  pytest-3 main.py

Or you can run only one test, e. g.::

  env python3 main.py TestScriptsExecutable
  pytest-3 -k TestScriptsExecutable main.py
"""

import importlib.metadata
import os
import re
import shutil
import subprocess
import tempfile
import unittest


class TestScriptsExecutable(unittest.TestCase):
    """
    :Author: Daniel Mohr
    :Date: 2025-02-27

    env python3 main.py TestScriptsExecutable
    pytest-3 -k TestScriptsExecutable main.py
    """
    subprocess_timeout = 42

    def test_yaml2script(self):
        """
        yaml2script

        :Author: Daniel Mohr
        :Date: 2025-02-26

        env python3 main.py \
          TestScriptsExecutable.test_yaml2script
        """
        cpi = subprocess.run(
            "yaml2script",
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            shell=True, timeout=self.subprocess_timeout, check=False)
        with self.assertRaises(subprocess.CalledProcessError):
            # parameter is necessary
            cpi.check_returncode()

    def test_yaml2script_version(self):
        """
        yaml2script version

        :Author: Daniel Mohr
        :Date: 2025-02-26

        env python3 main.py \
          TestScriptsExecutable.test_yaml2script_version
        """
        cpi = subprocess.run(
            "yaml2script version",
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            shell=True, timeout=self.subprocess_timeout, check=True)
        try:
            version = importlib.metadata.version('yaml2script')
        except importlib.metadata.PackageNotFoundError:
            # e. g. yaml2script is installed via pipx
            version = None
        if version is None:
            self.assertTrue(
                cpi.stdout.strip().decode().startswith('yaml2script version '))
        else:
            self.assertEqual(cpi.stdout.strip().decode(),
                             f'yaml2script version {version}')

    def test_yaml2script_extract_01(self):
        """
        yaml2script extract 01

        :Author: Daniel Mohr
        :Date: 2025-02-26

        env python3 main.py \
          TestScriptsExecutable.test_yaml2script_extract_01
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copyfile(
                os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    'data/01_gitlab-ci.yaml'),
                os.path.join(tmpdir, '.gitlab-ci.yml'))
            cpi = subprocess.run(
                "yaml2script extract .gitlab-ci.yml pre-commit",
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir, timeout=self.subprocess_timeout,
                check=True)
            filename = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                'data/01_extract_pre-commit')
            with open(filename, encoding='utf8') as fide:
                data = fide.read()
            self.assertEqual(cpi.stdout.decode(),
                             data)

    def test_yaml2script_check_01(self):
        """
        yaml2script check 01

        :Author: Daniel Mohr
        :Date: 2025-02-26

        env python3 main.py \
          TestScriptsExecutable.test_yaml2script_check_01
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copyfile(
                os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    'data/01_gitlab-ci.yaml'),
                os.path.join(tmpdir, '.gitlab-ci.yml'))
            subprocess.run(
                "yaml2script check .gitlab-ci.yml pre-commit",
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir, timeout=self.subprocess_timeout,
                check=True)

    def test_yaml2script_all_01(self):
        """
        yaml2script all 01

        :Author: Daniel Mohr
        :Date: 2025-02-27

        env python3 main.py \
          TestScriptsExecutable.test_yaml2script_all_01
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copyfile(
                os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    'data/01_gitlab-ci.yaml'),
                os.path.join(tmpdir, '.gitlab-ci.yml'))
            subprocess.run(
                "yaml2script all .gitlab-ci.yml",
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir, timeout=self.subprocess_timeout,
                check=True)

    def test_pre_commit_yaml2script_check_01(self):
        """
        pre-commit yaml2script check 01

        :Author: Daniel Mohr
        :Date: 2025-02-26

        env python3 main.py \
          TestScriptsExecutable.test_pre_commit_yaml2script_check_01
        """
        with tempfile.TemporaryDirectory() as repodir:
            subprocess.run(
                "git clone --bare . " + repodir,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True,
                cwd=os.path.realpath(os.path.join(
                    os.path.dirname(__file__),
                    '../')),
                timeout=self.subprocess_timeout,
                check=True)
            subprocess.run(
                "git tag -f latest",
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=repodir, timeout=self.subprocess_timeout,
                check=False)
            with tempfile.TemporaryDirectory() as tmpdir:
                subprocess.run(
                    "git init " + tmpdir,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True, cwd=tmpdir, timeout=self.subprocess_timeout,
                    check=True)
                shutil.copyfile(
                    os.path.join(
                        os.path.dirname(os.path.realpath(__file__)),
                        'data/01_gitlab-ci.yaml'),
                    os.path.join(tmpdir, '.gitlab-ci.yml'))
                filename = os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    'data/01_pre-commit-config.yaml')
                with open(filename, encoding='utf8') as fide:
                    data = fide.read()
                data = re.sub("repo_dir", repodir, data)
                filename = os.path.join(tmpdir, '.pre-commit-config.yaml')
                with open(filename, 'w', encoding='utf8') as fide:
                    fide.write(data)
                subprocess.run(
                    "git add .",
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True, cwd=tmpdir, timeout=self.subprocess_timeout,
                    check=True)
                subprocess.run(
                    "pre-commit run --all-files",
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True, cwd=tmpdir, timeout=10*self.subprocess_timeout,
                    check=True)

    def test_yaml2script_extract_02(self):
        """
        yaml2script extract 02

        :Author: Daniel Mohr
        :Date: 2025-02-26

        env python3 main.py \
          TestScriptsExecutable.test_yaml2script_extract_02
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copyfile(
                os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    'data/02_gitlab-ci.yaml'),
                os.path.join(tmpdir, '.gitlab-ci.yml'))
            cpi = subprocess.run(
                "yaml2script extract -shebang='#!/usr/bin/env python' "
                ".gitlab-ci.yml my_python-job",
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir, timeout=self.subprocess_timeout,
                check=True)
            filename = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                'data/02_extract_my_python-job')
            with open(filename, encoding='utf8') as fide:
                data = fide.read()
            self.assertEqual(cpi.stdout.decode(),
                             data)

    def test_yaml2script_check_02(self):
        """
        yaml2script check 02

        :Author: Daniel Mohr
        :Date: 2025-02-26

        env python3 main.py \
          TestScriptsExecutable.test_yaml2script_check_02
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copyfile(
                os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    'data/02_gitlab-ci.yaml'),
                os.path.join(tmpdir, '.gitlab-ci.yml'))
            subprocess.run(
                "yaml2script check -shebang='#!/usr/bin/env python' "
                "-check_command=pycodestyle -parameter_check_command='' "
                ".gitlab-ci.yml my_python-job",
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir, timeout=self.subprocess_timeout,
                check=True)

    def test_yaml2script_all_02(self):
        """
        yaml2script all 02

        :Author: Daniel Mohr
        :Date: 2025-02-27

        env python3 main.py \
          TestScriptsExecutable.test_yaml2script_all_02
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copyfile(
                os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    'data/02_gitlab-ci.yaml'),
                os.path.join(tmpdir, '.gitlab-ci.yml'))
            subprocess.run(
                "yaml2script all -shebang='#!/usr/bin/env python' "
                "-check_command=pycodestyle -parameter_check_command='' "
                ".gitlab-ci.yml",
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir, timeout=self.subprocess_timeout,
                check=True)

    def test_pre_commit_yaml2script_check_02(self):
        """
        pre-commit yaml2script check 02

        :Author: Daniel Mohr
        :Date: 2025-02-26

        env python3 main.py \
          TestScriptsExecutable.test_pre_commit_yaml2script_check_02
        """
        with tempfile.TemporaryDirectory() as repodir:
            subprocess.run(
                "git clone --bare . " + repodir,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True,
                cwd=os.path.realpath(os.path.join(
                    os.path.dirname(__file__),
                    '../')),
                timeout=self.subprocess_timeout,
                check=True)
            subprocess.run(
                "git tag -f latest",
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=repodir, timeout=self.subprocess_timeout,
                check=False)
            with tempfile.TemporaryDirectory() as tmpdir:
                subprocess.run(
                    "git init " + tmpdir,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True, cwd=tmpdir, timeout=self.subprocess_timeout,
                    check=True)
                shutil.copyfile(
                    os.path.join(
                        os.path.dirname(os.path.realpath(__file__)),
                        'data/02_gitlab-ci.yaml'),
                    os.path.join(tmpdir, '.gitlab-ci.yml'))
                filename = os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    'data/02_pre-commit-config.yaml')
                with open(filename, encoding='utf8') as fide:
                    data = fide.read()
                data = re.sub("repo_dir", repodir, data)
                filename = os.path.join(tmpdir, '.pre-commit-config.yaml')
                with open(filename, 'w', encoding='utf8') as fide:
                    fide.write(data)
                subprocess.run(
                    "git add .",
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True, cwd=tmpdir, timeout=self.subprocess_timeout,
                    check=True)
                subprocess.run(
                    "pre-commit run --all-files",
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True, cwd=tmpdir, timeout=10*self.subprocess_timeout,
                    check=True)

    def test_yaml2script_extract_03(self):
        """
        yaml2script extract 03

        :Author: Daniel Mohr
        :Date: 2025-02-27

        env python3 main.py \
          TestScriptsExecutable.test_yaml2script_extract_03
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copyfile(
                os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    'data/03_gitlab-ci.yaml'),
                os.path.join(tmpdir, '.gitlab-ci.yml'))
            cpi = subprocess.run(
                "yaml2script extract .gitlab-ci.yml ruff",
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir, timeout=self.subprocess_timeout,
                check=True)
            filename = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                'data/03_extract_ruff')
            with open(filename, encoding='utf8') as fide:
                data = fide.read()
            self.assertEqual(cpi.stdout.decode(),
                             data)

    def test_yaml2script_check_03(self):
        """
        yaml2script check 03

        :Author: Daniel Mohr
        :Date: 2025-02-27

        env python3 main.py \
          TestScriptsExecutable.test_yaml2script_check_03
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copyfile(
                os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    'data/03_gitlab-ci.yaml'),
                os.path.join(tmpdir, '.gitlab-ci.yml'))
            cpi = subprocess.run(
                "yaml2script check .gitlab-ci.yml ruff",
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir, timeout=self.subprocess_timeout,
                check=False)
            with self.assertRaises(subprocess.CalledProcessError):
                cpi.check_returncode()

    def test_yaml2script_all_03(self):
        """
        yaml2script all 03

        :Author: Daniel Mohr
        :Date: 2025-02-27

        env python3 main.py \
          TestScriptsExecutable.test_yaml2script_all_03
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copyfile(
                os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    'data/03_gitlab-ci.yaml'),
                os.path.join(tmpdir, '.gitlab-ci.yml'))
            cpi = subprocess.run(
                "yaml2script all .gitlab-ci.yml",
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir, timeout=self.subprocess_timeout,
                check=False)
            with self.assertRaises(subprocess.CalledProcessError):
                cpi.check_returncode()

    def test_pre_commit_yaml2script_all_03(self):
        """
        pre-commit yaml2script all 03

        :Author: Daniel Mohr
        :Date: 2025-02-27

        env python3 main.py \
          TestScriptsExecutable.test_pre_commit_yaml2script_all_03
        """
        with tempfile.TemporaryDirectory() as repodir:
            subprocess.run(
                "git clone --bare . " + repodir,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True,
                cwd=os.path.realpath(os.path.join(
                    os.path.dirname(__file__),
                    '../')),
                timeout=self.subprocess_timeout,
                check=True)
            subprocess.run(
                "git tag -f latest",
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=repodir, timeout=self.subprocess_timeout,
                check=False)
            with tempfile.TemporaryDirectory() as tmpdir:
                subprocess.run(
                    "git init " + tmpdir,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True, cwd=tmpdir, timeout=self.subprocess_timeout,
                    check=True)
                shutil.copyfile(
                    os.path.join(
                        os.path.dirname(os.path.realpath(__file__)),
                        'data/03_gitlab-ci.yaml'),
                    os.path.join(tmpdir, '.gitlab-ci.yml'))
                filename = os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    'data/03_pre-commit-config.yaml')
                with open(filename, encoding='utf8') as fide:
                    data = fide.read()
                data = re.sub("repo_dir", repodir, data)
                filename = os.path.join(tmpdir, '.pre-commit-config.yaml')
                with open(filename, 'w', encoding='utf8') as fide:
                    fide.write(data)
                subprocess.run(
                    "git add .",
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True, cwd=tmpdir, timeout=self.subprocess_timeout,
                    check=True)
                cpi = subprocess.run(
                    "pre-commit run --all-files",
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True, cwd=tmpdir, timeout=10*self.subprocess_timeout,
                    check=False)
                with self.assertRaises(subprocess.CalledProcessError):
                    cpi.check_returncode()

    def test_yaml2script_all_04(self):
        """
        yaml2script all 04

        :Author: Daniel Mohr
        :Date: 2025-02-27

        env python3 main.py \
          TestScriptsExecutable.test_yaml2script_all_04
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copyfile(
                os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    'data/04_gitlab-ci.yaml'),
                os.path.join(tmpdir, '.gitlab-ci.yml'))
            subprocess.run(
                "yaml2script all .gitlab-ci.yml",
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir, timeout=self.subprocess_timeout,
                check=True)

    def test_pre_commit_yaml2script_all_04(self):
        """
        pre-commit yaml2script all 04

        :Author: Daniel Mohr
        :Date: 2025-02-27

        env python3 main.py \
          TestScriptsExecutable.test_pre_commit_yaml2script_all_04
        """
        with tempfile.TemporaryDirectory() as repodir:
            subprocess.run(
                "git clone --bare . " + repodir,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True,
                cwd=os.path.realpath(os.path.join(
                    os.path.dirname(__file__),
                    '../')),
                timeout=self.subprocess_timeout,
                check=True)
            subprocess.run(
                "git tag -f latest",
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=repodir, timeout=self.subprocess_timeout,
                check=False)
            with tempfile.TemporaryDirectory() as tmpdir:
                subprocess.run(
                    "git init " + tmpdir,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True, cwd=tmpdir, timeout=self.subprocess_timeout,
                    check=True)
                shutil.copyfile(
                    os.path.join(
                        os.path.dirname(os.path.realpath(__file__)),
                        'data/04_gitlab-ci.yaml'),
                    os.path.join(tmpdir, '.gitlab-ci.yml'))
                filename = os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    'data/04_pre-commit-config.yaml')
                with open(filename, encoding='utf8') as fide:
                    data = fide.read()
                data = re.sub("repo_dir", repodir, data)
                filename = os.path.join(tmpdir, '.pre-commit-config.yaml')
                with open(filename, 'w', encoding='utf8') as fide:
                    fide.write(data)
                subprocess.run(
                    "git add .",
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True, cwd=tmpdir, timeout=self.subprocess_timeout,
                    check=True)
                subprocess.run(
                    "pre-commit run --all-files",
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True, cwd=tmpdir, timeout=10*self.subprocess_timeout,
                    check=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
