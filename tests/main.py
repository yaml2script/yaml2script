"""
:Author: Daniel Mohr
:Email: daniel.mohr@uni-greifswald.de
:Date: 2026-06-09
:License: GPL-3.0-or-later

aggregation of tests

You can run this file directly::

  env python3 main.py
  pytest-3 main.py

Or you can run only one test, e. g.::

  env python3 main.py TestModule
  pytest-3 -k TestModule main.py

  env python3 main.py TestScriptsExecutable
  pytest-3 -k TestScriptsExecutable main.py
"""

import importlib
import importlib.metadata
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import MagicMock, Mock


class TestModule(unittest.TestCase):
    """
    :Author: Daniel Mohr
    :Date: 2026-06-09

    env python3 main.py TestModule
    pytest-3 -k TestModule main.py
    """
    @classmethod
    def setUpClass(cls):
        # pylint: disable = import-outside-toplevel
        try:
            cls.y2s_module = importlib.import_module(
                'yaml2script.script.yaml2script')
        except ImportError:
            cls.y2s_module = None

    def test_flatten_list(self):
        """
        simple test for `_flatten_list`

        :Author: Daniel Mohr
        :Date: 2026-06-09

        env python3 main.py TestModule.test_flatten_list
        """
        if self.y2s_module is None:
            # skip test in `pipx` installation
            self.skipTest(
                "yaml2script module not importable in current environment")

        # pylint: disable = protected-access
        _flatten_list = self.y2s_module._flatten_list
        _ReferenceClass = \
            self.y2s_module._ReferenceClass  # pylint: disable = invalid-name

        # simple nested list
        nested_list = [1, [2, 3], [4, [5, 6]]]
        expected = [1, 2, 3, 4, 5, 6]
        self.assertEqual(_flatten_list(nested_list, {}), expected)
        # empty list
        self.assertEqual(_flatten_list([], {}), [])
        # flat list
        flat_list = [1, 2, 3, 4]
        self.assertEqual(_flatten_list(flat_list, {}), flat_list)
        # simple reference class
        ref_list = [1, _ReferenceClass(None, None), 4]
        expected = [1, '', 4]
        self.assertEqual(_flatten_list(ref_list, {}), expected)

    def test_flatten_list_missing_reference(self):
        """
        test for `_flatten_list` (missing reference)

        :Author: Daniel Mohr
        :Date: 2026-06-09

        env python3 main.py TestModule.test_flatten_list_missing_reference
        """
        if self.y2s_module is None:
            # skip test in `pipx` installation
            self.skipTest(
                "yaml2script module not importable in current environment")

        # pylint: disable = protected-access
        _flatten_list = self.y2s_module._flatten_list
        _ReferenceClass = \
            self.y2s_module._ReferenceClass  # pylint: disable = invalid-name

        mock_node = MagicMock()
        mock_val_0 = Mock()
        mock_val_0.value = 'job1'
        mock_val_1 = Mock()
        mock_val_1.value = 'setting1'
        mock_node.value = [mock_val_0, mock_val_1]
        ref_instance = _ReferenceClass(loader=None, node=mock_node)
        test_list = [ref_instance]
        data = {}
        expected_msg = '# reference [job1, setting1] not defined in this file'
        with self.assertWarnsRegex(UserWarning, re.escape(expected_msg)):
            result = _flatten_list(test_list, data)
            self.assertEqual(result, [expected_msg])

    def test_flatten_list_job_missing(self):
        """
        test for `_flatten_list` (missing job)

        :Author: Daniel Mohr
        :Date: 2026-06-09

        env python3 main.py TestModule.test_flatten_list_job_missing
        """
        if self.y2s_module is None:
            # skip test in `pipx` installation
            self.skipTest(
                "yaml2script module not importable in current environment")

        # pylint: disable = protected-access
        _flatten_list = self.y2s_module._flatten_list
        _ReferenceClass = \
            self.y2s_module._ReferenceClass  # pylint: disable = invalid-name

        mock_node = MagicMock()
        mock_val_0 = Mock()
        mock_val_0.value = 'job1'
        mock_val_1 = Mock()
        mock_val_1.value = 'missing_key'
        mock_node.value = [mock_val_0, mock_val_1]
        ref_instance = _ReferenceClass(loader=None, node=mock_node)
        test_list = [ref_instance]
        data = {'job1': {'other_key': 'value'}}
        expected_msg = \
            '# reference: job "job1" has no "missing_key" in this file'
        with self.assertWarnsRegex(UserWarning, re.escape(expected_msg)):
            result = _flatten_list(test_list, data)
            self.assertEqual(result, [expected_msg])

    def test_read_yaml(self):
        """
        test `_read_yaml`

        :Author: Daniel Mohr
        :Date: 2026-06-09

        env python3 main.py TestModule.test_read_yaml
        """
        if self.y2s_module is None:
            # skip test in `pipx` installation
            self.skipTest(
                "yaml2script module not importable in current environment")

        # pylint: disable = protected-access
        _read_yaml = self.y2s_module._read_yaml

        # test successful YAML reading
        filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'data/04_pre-commit-config.yaml')
        data = _read_yaml(filename)
        self.assertIsInstance(data, dict)
        self.assertIn('repos', data)
        self.assertEqual(len(data['repos']), 1)
        self.assertEqual(data['repos'][0]['repo'], 'repo_dir')

        # test reading non-YAML file (should raise ValueError)
        with self.assertRaises(FileNotFoundError):
            _read_yaml('foo')

        # test reading another non-YAML file (should raise ValueError)
        filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'main.py')
        with self.assertRaises(ValueError):
            _read_yaml(filename)


class TestScriptsExecutable(unittest.TestCase):
    # pylint: disable = too-many-public-methods
    """
    :Author: Daniel Mohr
    :Date: 2026-06-09

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

    def test_yaml2script_help_output(self):
        """
        yaml2script

        :Author: Daniel Mohr
        :Date: 2025-02-28

        env python3 main.py \
          TestScriptsExecutable.test_yaml2script_help_output
        """
        cpi = subprocess.run(
            "yaml2script -h",
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            shell=True, timeout=self.subprocess_timeout, check=True)
        self.assertTrue(
            cpi.stdout.strip().decode().endswith(
                'License: GNU General Public License Version 3 '
                'or any later version (GPLv3+)'))

    def test_yaml2script_version(self):
        """
        yaml2script version

        :Author: Daniel Mohr
        :Date: 2025-02-28

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
        cpi = subprocess.run(
            "yaml2script version -o",
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            shell=True, timeout=self.subprocess_timeout, check=True)
        if version is not None:
            self.assertEqual(cpi.stdout.strip().decode(), version)
        cpi = subprocess.run(
            "yaml2script version -json",
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            shell=True, timeout=self.subprocess_timeout, check=True)
        data = json.loads(cpi.stdout.decode())
        self.assertEqual(data["Name"], "yaml2script")
        if version is not None:
            self.assertEqual(data["Version"], version)

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

    def test_yaml2script_check_03_ignore(self):
        """
        yaml2script check 03

        :Author: Daniel Mohr
        :Date: 2025-02-28

        env python3 main.py \
          TestScriptsExecutable.test_yaml2script_check_03_ignore
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copyfile(
                os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    'data/03_gitlab-ci.yaml'),
                os.path.join(tmpdir, '.gitlab-ci.yml'))
            subprocess.run(
                "yaml2script check -verbose .gitlab-ci.yml ruff "
                "-parameter_check_command '-e SC2028'",
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir, timeout=self.subprocess_timeout,
                check=True)

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

    def test_yaml2script_all_03_ignore(self):
        """
        yaml2script all 03

        :Author: Daniel Mohr
        :Date: 2025-02-28

        env python3 main.py \
          TestScriptsExecutable.test_yaml2script_all_03_ignore
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copyfile(
                os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    'data/03_gitlab-ci.yaml'),
                os.path.join(tmpdir, '.gitlab-ci.yml'))
            subprocess.run(
                "yaml2script all -verbose .gitlab-ci.yml "
                "-parameter_check_command '-e SC2028'",
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir, timeout=self.subprocess_timeout,
                check=True)

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

    def test_yaml2script_all_04_05(self):
        """
        yaml2script all 04
        yaml2script all 05

        :Author: Daniel Mohr
        :Date: 2025-03-06

        env python3 main.py \
          TestScriptsExecutable.test_yaml2script_all_04_05
        """
        for yamlfile in ['data/04_gitlab-ci.yaml', 'data/05_gitlab-ci.yaml']:
            with tempfile.TemporaryDirectory() as tmpdir:
                shutil.copyfile(
                    os.path.join(
                        os.path.dirname(os.path.realpath(__file__)),
                        yamlfile),
                    os.path.join(tmpdir, '.gitlab-ci.yml'))
                subprocess.run(
                    "yaml2script all .gitlab-ci.yml",
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True, cwd=tmpdir, timeout=self.subprocess_timeout,
                    check=True)

    def test_pre_commit_yaml2script_all_04_05(self):
        """
        pre-commit yaml2script all 04
        pre-commit yaml2script all 05

        :Author: Daniel Mohr
        :Date: 2025-03-06

        env python3 main.py \
          TestScriptsExecutable.test_pre_commit_yaml2script_all_04_05
        """
        for (gitlabcifile, precommitfile) in [
                ('data/04_gitlab-ci.yaml', 'data/04_pre-commit-config.yaml'),
                ('data/05_gitlab-ci.yaml', 'data/05_pre-commit-config.yaml')]:
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
                        shell=True, cwd=tmpdir,
                        timeout=self.subprocess_timeout,
                        check=True)
                    shutil.copyfile(
                        os.path.join(
                            os.path.dirname(os.path.realpath(__file__)),
                            gitlabcifile),
                        os.path.join(tmpdir, '.gitlab-ci.yml'))
                    filename = os.path.join(
                        os.path.dirname(os.path.realpath(__file__)),
                        precommitfile)
                    with open(filename, encoding='utf8') as fide:
                        data = fide.read()
                    data = re.sub("repo_dir", repodir, data)
                    filename = os.path.join(tmpdir, '.pre-commit-config.yaml')
                    with open(filename, 'w', encoding='utf8') as fide:
                        fide.write(data)
                    subprocess.run(
                        "git add .",
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        shell=True, cwd=tmpdir,
                        timeout=self.subprocess_timeout,
                        check=True)
                    subprocess.run(
                        "pre-commit run --all-files",
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        shell=True, cwd=tmpdir,
                        timeout=10*self.subprocess_timeout,
                        check=True)

    def test_yaml2script_all_06(self):
        """
        yaml2script all 06

        test if yaml2script correctly handles hidden jobs and
        document markers (---/...).

        :Author: Daniel Mohr
        :Date: 2026-06-09

        env python3 main.py \
          TestScriptsExecutable.test_yaml2script_all_06
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copyfile(
                os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    'data/06_gitlab-ci.yaml'),
                os.path.join(tmpdir, '.gitlab-ci.yml'))
            subprocess.run(
                "yaml2script all .gitlab-ci.yml",
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir, timeout=self.subprocess_timeout,
                check=True)

    def test_yaml2script_extract_06(self):
        """
        yaml2script all 06

        test if yaml2script raises a clear error for invalid jobnames

        :Author: Daniel Mohr
        :Date: 2026-06-09

        env python3 main.py \
          TestScriptsExecutable.test_yaml2script_extract_06
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copyfile(
                os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    'data/06_gitlab-ci.yaml'),
                os.path.join(tmpdir, '.gitlab-ci.yml'))
            cpi = subprocess.run(
                "yaml2script extract .gitlab-ci.yml invalid_job",
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=tmpdir, timeout=self.subprocess_timeout,
                check=False)
            self.assertEqual(cpi.returncode, 1)
            self.assertIn("job 'invalid_job' not found", cpi.stderr.decode())


if __name__ == '__main__':
    unittest.main(verbosity=2)
