import copy

import yaml

from ..config_validation import main as validate


def test_minimal_config():
    data = {
        'project_source': '/path/to/project/',
        'working_dir': 'results/',
        'base_config': '/path/to/project/config.yaml'
    }
    validate(data)

    assert data == {
        'project_source': '/path/to/project/',
        'working_dir': 'results/',
        'base_config': '/path/to/project/config.yaml',
        'extra_parameters': {'repetitions': 1},
        'exec_command': [],
        'result_dirs': [],
        'symlinks': []
    }


def test_maximal_config():
    data = yaml.load("""
project_source: '/path/to/project/'
working_dir: 'output/'

exec_command:
    - snakemake -pr
result_dirs:
    - images
    - results

base_config: '/path/to/project/config.yaml'
symlinks:
    - ../data/
config_parameters:
    - key: param1
      values: [0, 1, 2, d]
      paired:
        - key: param2
          values: [a, b, c, 6]
    - key: [nested, param3]
      values: ['a', 'b', 'c']
extra_parameters:
    git_branch: ['master']
    repetitions: 1
    """)
    orig_data = copy.deepcopy(data)

    validate(data)
    assert data == orig_data
