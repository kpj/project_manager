import os

import anyconfig
from tqdm import tqdm

from ..utils import SECTION_SEPARATOR, TEMP_CONFIG_NAME, load_config


def main(config_path: str, dry: bool):
    config = load_config(config_path)

    for entry in tqdm(
        os.scandir(config['working_dir']),
        total=len(os.listdir(config['working_dir']))
    ):
        if not entry.name.startswith(f'run{SECTION_SEPARATOR}'):
            continue

        # switch to correct directory
        print(entry.name)
        wd = os.getcwd()
        os.chdir(entry.path)

        # load config
        conf_name = (TEMP_CONFIG_NAME
                     if config['base_config'] is None
                     else os.path.basename(config['base_config']))
        cur_config = anyconfig.load(conf_name)

        # execute commands
        for cmd in config['exec_command']:
            cmd_mod = cmd.format(**cur_config)

            print(f' > {cmd_mod}')
            if not dry:
                os.system(cmd_mod)

        os.chdir(wd)
