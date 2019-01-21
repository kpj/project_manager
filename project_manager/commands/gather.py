import os
import shutil

from ..utils import load_config


def main(config_path: str, output: str) -> None:
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
