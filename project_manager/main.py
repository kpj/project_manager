"""
Automatically span a matrix of configurations using the `build` command.
Then execute each pipeline using `run`.
And finally aggregate the obtained results using the `gather` command.
"""

import os
import sys
import copy
import shutil
import operator
import functools
import itertools

from pprint import pprint

import sh
import yaml
import click

from tqdm import tqdm


def load_config(fname):
    with open(fname) as fd:
        return yaml.load(fd)


def get_by_keylist(root, items):
    return functools.reduce(operator.getitem, items, root)


def set_by_keylist(root, items, value):
    get_by_keylist(root, items[:-1])[items[-1]] = value


def assign_to_dict(dict_, key, value):
    if isinstance(key, list):
        set_by_keylist(dict_, key, value)
    else:
        dict_[key] = value


def dict_to_keyset(d):
    all_keys = set()
    for k, v in d.items():
        if isinstance(v, dict):
            cur = (k, dict_to_keyset(v))
        else:
            cur = k
        all_keys.add(cur)
    return frozenset(all_keys)


@click.group()
def cli() -> None:
    """Automate multi-config simulation runs."""
    pass


@cli.command(help='Setup environments.')
@click.option(
    '--config', '-c', 'config_path', default='config.yaml',
    type=click.Path(exists=True, dir_okay=False), help='Config file to use.')
@click.option(
    '--dry', '-d', default=False, is_flag=True,
    help='Conduct dry run.')
def build(config_path: str, dry: bool) -> None:
    config = load_config(config_path)
    base_config = load_config(config['base_config'])

    # if needed prepare environment
    if not dry:
        shutil.rmtree(config['working_dir'], ignore_errors=True)
        os.makedirs(config['working_dir'])

        exec_dir = os.getcwd()
        os.chdir(config['working_dir'])

    # setup and run schedule
    special_extra_keys = ['repetitions']  # these get handled individually

    config_schedule = []
    for entry in config['config_parameters']:
        tmp = []

        # handle possible pairing
        if 'paired' in entry:
            # sanity checks
            for e in entry['paired']:
                if len(e['values']) != len(entry['values']):
                    raise RuntimeError(f'Invalid pairing for "{e["key"]}"')

            # generate associations
            paired_data = []
            for i in range(len(entry['values'])):
                case_values = [(c['key'], c['values'][i])
                               for c in entry['paired']]

                paired_data.append([{
                    'key': key,
                    'value': val
                } for key, val in case_values])
        else:
            paired_data = [None] * len(entry['values'])

        # add to schedule
        for val, pair in zip(entry['values'], paired_data):
            tmp.append(('config', entry['key'], val, pair))
        config_schedule.append(tmp)

    # TODO: make config handling better
    if 'extra_parameters' in config:
        extra_schedule = [[('extra', k, v, None) for v in vs]
                          for k, vs in config['extra_parameters'].items()
                          if k not in special_extra_keys]
    else:
        extra_schedule = []
    schedule = config_schedule + extra_schedule

    for spec in tqdm(
        itertools.product(*schedule),
        total=functools.reduce(operator.mul, [len(s) for s in schedule], 1),
        desc='Setting up environments'
    ):
        # create custom config
        cur_conf = copy.deepcopy(base_config)

        for t, k, v, p in spec:
            if t != 'config':
                continue

            # set main parameter
            assign_to_dict(cur_conf, k, v)

            # set potential paired parameters
            if p is not None:
                for entry in p:
                    k, v = entry['key'], entry['value']
                    assign_to_dict(cur_conf, k, v)

        # assert subset relation (so only valid keys are used)
        cur_keys = dict_to_keyset(cur_conf)
        base_keys = dict_to_keyset(base_config)
        if cur_keys != base_keys:
            msg = 'Generated config is invalid.\n'

            only_cur = cur_keys - base_keys
            msg += 'Only in generated config:\n'
            for k in only_cur:
                msg += f' > {k}\n'

            raise RuntimeError(msg)

        # make spec sortable
        c = lambda x: '+'.join(x) if isinstance(x, list) else x
        c2 = lambda x: x.replace('/', '_')

        spec = [(t, c(k), v, p) for t, k, v, p in spec]

        # extract extra info
        extra_info = {k: v for t, k, v, p in sorted(spec) if t == 'extra'}

        # TODO: make config handling better
        if (
            'extra_parameters' not in config or
            'repetitions' not in config['extra_parameters']
        ):
            repetition_count = 1
        else:
            repetition_count = config['extra_parameters']['repetitions']

        for rep in range(repetition_count):
            # assemble index
            idx = ';'.join([f'{k}:{c2(v)}' for t, k, v, p in sorted(spec)])
            rep_app = f';repetition:{rep+1}' if repetition_count > 1 else ''
            target_dir = f'run__{idx}{rep_app}'

            # abort if in dry run
            if dry:
                print(target_dir)
                pprint(cur_conf)
                pprint(extra_info)
                print()
                continue

            # setup environment
            if os.path.isdir(
                os.path.join(exec_dir, config['project_source'])
            ):
                shutil.copytree(
                    os.path.join(exec_dir, config['project_source']),
                    target_dir)
            else:
                sh.git.clone(config['project_source'], target_dir)

            if 'git_branch' in extra_info:
                sh.git.checkout(extra_info['git_branch'], _cwd=target_dir)

            conf_name = os.path.basename(config['base_config'])
            with open(f'{target_dir}/{conf_name}', 'w') as fd:
                yaml.dump(cur_conf, fd)

            if 'symlinks' in config:
                for sym in config['symlinks']:
                    sym_path = os.path.relpath(os.path.join(
                        exec_dir, os.path.dirname(config_path), sym),
                        start=target_dir)
                    if not os.path.exists(os.path.join(target_dir, sym_path)):
                        print(f'Cannot find "{sym_path}"')

                    sym_base = os.path.basename(os.path.normpath(sym))

                    os.symlink(
                        sym_path, os.path.join(target_dir, sym_base),
                        target_is_directory=os.path.isdir(sym))


@cli.command(help='Run simulations in each environment.')
@click.option(
    '--config', '-c', 'config_path', default='config.yaml',
    type=click.Path(exists=True, dir_okay=False), help='Config file to use.')
@click.option(
    '--dry', '-d', default=False, is_flag=True,
    help='Conduct dry run.')
def run(config_path: str, dry: bool) -> None:
    config = load_config(config_path)

    for entry in tqdm(
        os.scandir(config['working_dir']),
        total=len(os.listdir(config['working_dir']))
    ):
        if not entry.name.startswith('run__'):
            continue

        # switch to correct directory
        print(entry.name)
        wd = os.getcwd()
        os.chdir(entry.path)

        # execute commands
        for cmd in config['exec_command']:
            print(f' > {cmd}')
            if not dry:
                os.system(cmd)

        os.chdir(wd)


@cli.command(help='Gather results from each run.')
@click.option(
    '--config', '-c', 'config_path', default='config.yaml',
    type=click.Path(exists=True, dir_okay=False), help='Config file to use.')
@click.option(
    '--output', '-o', default=None,
    type=click.Path(exists=False, file_okay=False),
    help='Path to store aggregated results at.')
def gather(config_path: str, output: str) -> None:
    config = load_config(config_path)

    if output is None:
        target_dir = os.path.join(config['working_dir'], 'aggregated_results')
    else:
        target_dir = output

    shutil.rmtree(target_dir, ignore_errors=True)
    os.makedirs(target_dir)

    # iterate over individual pipeline runs
    for entry in os.scandir(config['working_dir']):
        if not entry.name.startswith('run__'):
            continue
        print(entry.name)

        # iterate over requested result directories
        for dir_ in config['result_dirs']:
            for file_ in os.scandir(
                os.path.join(entry.path, dir_)
            ):
                print(f' > {file_.name}')

                # assemble new filename
                raw_file, ext = os.path.splitext(file_)
                idx = entry.name[3:]
                suf_file = os.path.basename(raw_file) + idx + ext

                # extract file
                os.makedirs(os.path.join(target_dir, dir_), exist_ok=True)
                shutil.copyfile(
                    file_.path,
                    os.path.join(target_dir, dir_, suf_file))


if __name__ == '__main__':
    cli()
