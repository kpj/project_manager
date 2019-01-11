import os
import yaml


def main():
    with open('my_conf.yaml') as fd:
        config = yaml.load(fd)
    msg = config['message']

    os.makedirs('results')
    with open('results/data.txt', 'w') as fd:
        if msg is None:
            fd.write('special')
        else:
            fd.write(config['message'])


if __name__ == '__main__':
    main()
