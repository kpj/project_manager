import os
import shutil
import itertools

import yaml

import pytest
from click.testing import CliRunner

from ..main import cli
from ..commands import build
from ..utils import SECTION_SEPARATOR, PARAMETER_ASSIGNMENT, PARAMETER_SEPARATOR


def test_dummy():
    root = os.path.join(os.getcwd(), 'project_manager', 'tests')
    runner = CliRunner()

    with runner.isolated_filesystem():
        # setup environment
        root_iso = os.getcwd()
        shutil.copy(os.path.join(root, 'config.yaml'), 'config.yaml')
        shutil.copytree(os.path.join(root, 'dummy_project'), 'dummy_project')

        # run commands
        os.chdir(root_iso)
        result_build = runner.invoke(cli, ['build'], catch_exceptions=False)
        assert result_build.exit_code == 0

        os.chdir(root_iso)
        result_run = runner.invoke(cli, ['run'], catch_exceptions=False)
        assert result_run.exit_code == 0

        os.chdir(root_iso)
        result_gather = runner.invoke(cli, ['gather'], catch_exceptions=False)
        assert result_gather.exit_code == 0

        # check individual outputs
        assert len(os.listdir('tmp/')) == 12 + 1  # |run| + |agg|

        for entry in os.scandir('tmp/'):
            if not entry.name.startswith(f'run{SECTION_SEPARATOR}'):
                continue

            expected_data = dict([e.split(PARAMETER_ASSIGNMENT)
                                  for e in (entry.name
                                                 .split('.')[1]
                                                 .split(PARAMETER_SEPARATOR))])
            fname = {
                '1': 'foo.txt',
                '2': 'bar.md',
                '3': 'baz.rst'
            }[expected_data['number']]

            assert os.path.isfile(os.path.join(entry.path, fname))

        # check aggregated output
        os.chdir(root_iso)

        # based on filenames
        all_data = []
        for entry in os.scandir('tmp/aggregated_results/results/'):
            expected_data = dict([e.split(PARAMETER_ASSIGNMENT)
                                  for e in (entry.name
                                                 .split('.')[1]
                                                 .split(PARAMETER_SEPARATOR))])

            # handle special case (null/None in config)
            if expected_data['message'] == 'None':
                expected_data['message'] = 'special'

            with open(entry.path) as fd:
                data = fd.read()

            assert expected_data['message'] * int(expected_data['number']) == data
            all_data.append(data)

        # based on config
        with open('config.yaml') as fd:
            config = yaml.full_load(fd)

        expected_all_data = [
            m * n
            for m, n in itertools.product(
                *[[v if v is not None else 'special' for v in e['values']]
                  for e in config['config_parameters']])
        ]
        assert set(all_data) == set(expected_all_data)


def test_key_misspelling():
    runner = CliRunner()

    with runner.isolated_filesystem():
        # setup environment
        with open('my_conf.yaml', 'w') as fd:
            fd.write("""
actual_key: 42
another_key: foo
            """)

        with open('config.yaml', 'w') as fd:
            fd.write("""
project_source: fubar
working_dir: tmp
base_config: my_conf.yaml
config_parameters:
    - key: misspelled_key
      values: [invalid]
    - key: another_key
      values: [bar, baz, qux]
            """)

        # run commands
        with pytest.raises(RuntimeError, match='> misspelled_key'):
            build('config.yaml')


def test_mismatching_key_pairing_name():
    runner = CliRunner()

    with runner.isolated_filesystem():
        # setup environment
        with open('my_conf.yaml', 'w') as fd:
            fd.write("""
my_key: 1
other_key: a
            """)

        with open('config.yaml', 'w') as fd:
            fd.write("""
project_source: fubar
working_dir: tmp
base_config: my_conf.yaml
config_parameters:
    - key: my_key
      values: [2,3,4]
      paired:
          - key: other_key_wrong
            values: [b,c,d]
            """)

        # run commands
        with pytest.raises(
            RuntimeError,
            match='> other_key_wrong'
        ):
            build('config.yaml')


def test_mismatching_key_pairing_length():
    runner = CliRunner()

    with runner.isolated_filesystem():
        # setup environment
        with open('my_conf.yaml', 'w') as fd:
            fd.write("""
my_key: 1
other_key: a
            """)

        with open('config.yaml', 'w') as fd:
            fd.write("""
project_source: fubar
working_dir: tmp
base_config: my_conf.yaml
config_parameters:
    - key: my_key
      values: [2,3,4]
      paired:
          - key: other_key
            values: [b,c]
            """)

        # run commands
        with pytest.raises(
            RuntimeError,
            match='Invalid pairing for "my_key" & "other_key"'
        ):
            build('config.yaml')
