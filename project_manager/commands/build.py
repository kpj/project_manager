import os
import copy
import shutil
import operator
import functools
import itertools

from pprint import pprint

import sh
import anyconfig
from tqdm import tqdm

from ..utils import load_config, assign_to_dict, dict_to_keyset


def main(config_path: str, dry: bool = False):
    config = load_config(config_path)
    base_config = anyconfig.load(config['base_config'])

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
                    raise RuntimeError(
                        f'Invalid pairing for "{entry["key"]}" & "{e["key"]}"')

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

    extra_schedule = [[('extra', k, v, None) for v in vs]
                      for k, vs in config['extra_parameters'].items()
                      if k not in special_extra_keys]
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
        c = lambda x: '+'.join(x) if isinstance(x, list) else x  # noqa: E731
        c2 = lambda x: str(x).replace('/', '_')  # noqa: E731

        spec = [(t, c(k), v, p) for t, k, v, p in spec]

        # extract extra info
        extra_info = {k: v for t, k, v, p in sorted(spec) if t == 'extra'}
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
            anyconfig.dump(cur_conf, f'{target_dir}/{conf_name}')

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
