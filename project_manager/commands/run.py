import os

from tqdm import tqdm

from ..utils import SECTION_SEPARATOR, load_config


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

        # execute commands
        for cmd in config['exec_command']:
            print(f' > {cmd}')
            if not dry:
                os.system(cmd)

        os.chdir(wd)
