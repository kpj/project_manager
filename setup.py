from setuptools import setup, find_packages


setup(
    name='project_manager',
    version='0.0.1',

    description='A utility which makes running the same projects with various configurations as easy as pie',

    author='kpj',
    author_email='kpjkpjkpjkpjkpjkpj@gmail.com',

    packages=find_packages(exclude=['tests']),

    install_requires=[
        'pyyaml', 'pprint', 'sh', 'tqdm', 'click'
    ],

    entry_points={
        'console_scripts': [
            'project_manager=project_manager:cli',
        ]
    }
)
