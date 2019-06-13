Example
=======

A quick usage overview:

.. code-block:: bash

  $ tree
  .
  ├── config.yaml
  └── dummy_project
      ├── my_conf.yaml
      └── run.py

`config.yaml`:

.. code-block:: yaml

  project_source: dummy_project
  working_dir: tmp

  exec_command:
      - python3 run.py
  result_dirs:
      - results

  base_config: dummy_project/my_conf.yaml
  config_parameters:
      - key: message
        values: [A, B, C]

`dummy_project/my_conf.yaml`:

.. code-block:: yaml

  message: 'this is important'

`run.py`:

.. code-block:: python

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

We can then run the pipeline:

.. code-block:: bash

  $ project_manager build
  Setting up environments: 100%|██████████████████████████| 3/3 [00:00<00:00, 477.57it/s]
  $ project_manager run
  run.message=A
   > python3 run.py
  run.message=B
   > python3 run.py
  run.message=C
   > python3 run.py
  $ project_manager gather
  run.message=A
   > data.txt
  run.message=B
   > data.txt
  run.message=C
   > data.txt

Here's the result:

.. code-block:: bash

  $ tree tmp/
  tmp/
  ├── aggregated_results
  │   └── results
  │       ├── data.message=A.txt
  │       ├── data.message=B.txt
  │       └── data.message=C.txt
  ├── run.message=A
  │   ├── my_conf.yaml
  │   ├── results
  │   │   └── data.txt
  │   └── run.py
  ├── run.message=B
  │   ├── my_conf.yaml
  │   ├── results
  │   │   └── data.txt
  │   └── run.py
  └── run.message=C
      ├── my_conf.yaml
      ├── results
      │   └── data.txt
      └── run.py
  $ cat tmp/aggregated_results/results/*
  ABC
