import operator
import functools

import yaml

from .config_validation import main as validate


def load_config(fname):
    with open(fname) as fd:
        config = yaml.load(fd)

    return validate(config)


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
