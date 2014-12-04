gogeta_update
=============

Description
-----------

Given a YAML config file (`gogeta.yaml`), updates keys in etcd to allow gogeta to proxy hostnames to backends

Usage
-----

::

    usage: gogeta-configure [-h] [--debug] [--silent] [--update] [--list]
                            [--dry-run] [--purge] [--version]
                            [config_file]

    Update gogeta via etcd

    positional arguments:
      config_file    YAML config file (use "-" to read from STDIN)

    optional arguments:
      -h, --help     show this help message and exit
      --debug, -d    Show debug logging
      --silent, -s   Hide error logging
      --update, -u   Update services
      --list, -l     List services
      --dry-run, -D  Do not change configuration
      --purge        Purge all gogeta config from etcd
      --version, -v  show program's version number and exit

Example Config
--------------

::

    ---
    etcd: 127.0.0.1:4001
    services:
      bar.example.com:
      - backend-3.backend
      - backend-4.backend
      foo.example.com:
      - backend-1.backend
      - backend-2.backend

More examples are available in the examples folder of the source distribution

