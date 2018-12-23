Setting up the configuration file
=================================

Create a configuration:

.. code-block:: yaml

  project_source: <url or path>  # project you want to run
  working_dir: <path>  # where everything will run

  exec_command:  # list of commands that will be executed in each project setup
      - <python ..>
  result_dirs:  # list of files/folders that will be extracted after successful execution
      - <result dir>

  base_config: <path>  # path to the raw configuration file (typically part of your project)
  symlinks:  # list of symlinks to include in each project setup
      - <path 1>
      - <path 2>
  config_parameters:  # how to modify the configuration
      - key: param1
        values: [0, 1, 2]
        paired:
          - key: param2
            values: [a, b, c]
      - key: [nested, param3]
        values: ['a', 'b', 'c']
  extra_parameters:  # special extra parameters
      git_branch: ['master']
      repetitions: 1
