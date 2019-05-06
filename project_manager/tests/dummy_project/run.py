import os
import yaml


def main():
    with open('my_conf.yaml') as fd:
        config = yaml.load(fd)
    msg = config['message']
    num = config['number']

    os.makedirs('results')
    with open('results/data.txt', 'w') as fd:
        if msg is None:
            fd.write('special' * num)
        else:
            fd.write(config['message'] * num)

    with open('.'.join(config['extra']['filename']), 'w') as fd:
        fd.write('fubar')


if __name__ == '__main__':
    main()
