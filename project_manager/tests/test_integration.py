import os
import shutil

import yaml
from click.testing import CliRunner

from ..main import cli


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
            with open(entry.path) as fd:
                data = fd.read()

            assert expected_data == data
            all_data.append(data)

        with open('config.yaml') as fd:
            config = yaml.load(fd)
        expected_all_data = config['config_parameters'][0]['values']  # only one entry in list, thus this miust be the message
        assert set(all_data) == set(expected_all_data)
