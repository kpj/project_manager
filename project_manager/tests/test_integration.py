import os
import shutil

import yaml

import pytest
from click.testing import CliRunner

from ..main import cli
from ..commands import build


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
        result_build = runner.invoke(cli, ['build'])
        assert result_build.exit_code == 0

        os.chdir(root_iso)
        result_run = runner.invoke(cli, ['run'])
        assert result_run.exit_code == 0

        os.chdir(root_iso)
        result_gather = runner.invoke(cli, ['gather'])
        assert result_gather.exit_code == 0

        # check output
        os.chdir(root_iso)

        all_data = []
        for entry in os.scandir('tmp/aggregated_results/results/'):
            expected_data = entry.name.split('.')[0].split(':')[1]

            # handle special case (null/None in config)
            if expected_data == 'None':
                expected_data = 'special'

            with open(entry.path) as fd:
                data = fd.read()

            assert expected_data == data
            all_data.append(data)

        with open('config.yaml') as fd:
            config = yaml.load(fd)

        # only one entry in list, thus this must be the message
        expected_all_data = [v if v is not None else 'special'
                             for v in config['config_parameters'][0]['values']]
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
