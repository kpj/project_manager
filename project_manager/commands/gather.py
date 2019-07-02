import os
import shutil

from ..utils import SECTION_SEPARATOR, load_config


def copy_file(idx: str, fname: str, target_dir: str, sub_dir: str = '.') -> None:
    # assemble new filename
    raw_file, ext = os.path.splitext(fname)
    suf_file = os.path.basename(raw_file) + idx + ext

    # extract file
    os.makedirs(os.path.join(target_dir, sub_dir), exist_ok=True)
    shutil.copyfile(
        fname,
        os.path.join(target_dir, sub_dir, suf_file))


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
        if not entry.name.startswith(f'run{SECTION_SEPARATOR}'):
            continue
        print(entry.name)
        idx = entry.name[3:]

        # iterate over requested result files
        for res_file_ in config['result_files']:
            res_path = os.path.join(entry.path, res_file_)

            if os.path.isfile(res_path):
                print(f' > {res_file_}')
                copy_file(idx, res_path, target_dir)
            elif os.path.isdir(res_path):
                for file_ in os.scandir(res_path):
                    print(f' > {os.path.join(res_file_, file_.name)}')
                    copy_file(
                        idx, file_.path, target_dir,
                        sub_dir=res_file_)
            else:
                raise RuntimeError(f'Invalid file: "{res_path}"')
