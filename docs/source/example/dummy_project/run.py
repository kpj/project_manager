import os
import yaml


def main():
    with open('my_conf.yaml') as fd:
        config = yaml.full_load(fd)

    os.makedirs('results')
    with open('results/data.txt', 'w') as fd:
        fd.write(config['message'])


if __name__ == '__main__':
    main()
