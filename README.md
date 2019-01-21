# project_manager

[![pypi version](https://img.shields.io/pypi/v/project_manager.svg)](https://pypi.org/project/project_manager/)
[![license](https://img.shields.io/pypi/l/project_manager.svg)](https://pypi.org/project/project_manager/)

Easily run a project with various configuration setups.


## Installation

```bash
$ pip install project_manager
```


## Usage

Assuming that you have set up your [configuration file](https://project-manager.readthedocs.io/en/latest/setup_config.html) correctly,
a typical workflow could look like this:

```bash
$ project_manager build  # setup environment
[..]
$ project_manager run  # execute commands
[..]
$ project_manager gather  # aggregate results
[..]
```

For more information check out the [documentation](https://project-manager.readthedocs.io/).


## Development notes

Run tests:

```bash
$ pytest
```


Publish a new version to PyPi:

```bash
$ poetry --build publish
```
