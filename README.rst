===========
readcounter
===========


.. image:: https://img.shields.io/pypi/v/readcounter.svg
        :target: https://pypi.python.org/pypi/readcounter

.. image:: https://img.shields.io/travis/housw/readcounter.svg
        :target: https://travis-ci.org/housw/readcounter

.. image:: https://readthedocs.org/projects/readcounter/badge/?version=latest
        :target: https://readcounter.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status



**ReadCounter**: A read counting program support different input file and compression types.

* Free software: MIT license
* Documentation: https://readcounter.readthedocs.io.



Installation
------------

:install from github:

::

    $ git clone https://github.com/housw/readcounter.git && \
      cd readcounter && pip install -r requirements_dev.txt && python setup.py install



Usage
-----

:commands:

::

    $ readcounter --help

    Usage: readcounter [OPTIONS] COMMAND [ARGS]...

    Options:
        --help  Show this message and exit.

    Commands:
      bam
      fasta
      fastq
      fastqc

:bam subcommands:

- ``readcounter bam``

::

    $ readcounter bam --help

    Usage: readcounter bam [OPTIONS] INPUT_FILE

    Options:
        --min_read_len INTEGER          minimum read length  [default: 0]
        --min_aln_len INTEGER           minimum alignment length  [default: 0]
        --min_map_qual INTEGER          minimum mapping quality  [default: 0]
        --min_base_qual INTEGER         minimum base quality  [default: 0]
        --use_bamcov                    use bamcov for read counting  [default: False]
        --pysam_mem TEXT                maximum pysam memory  [default: 10G]
        -p, --prefix TEXT               output prefix
        -o, --output_dir TEXT           output directory  [default: ./]
        -f, --force                     force to overwrite the output file
        -l, --loglevel [critical|error|warning|info|debug]
        --version                       Show the version and exit.
        --help                          Show this message and exit.


:fasta subcommands:

- ``readcounter fasta``

::

    $ readcounter fasta --help

    Usage: readcounter fasta [OPTIONS] INPUT_FILE

    Options:
        -p, --prefix TEXT               output prefix
        -o, --output_dir TEXT           output directory  [default: ./]
        -f, --force                     force to overwrite the output file
        -l, --loglevel [critical|error|warning|info|debug]
        --version                       Show the version and exit.
        --help                          Show this message and exit.

:fastq subcommands:

- ``readcounter fastq``

::

    $ readcounter fastq --help

    Usage: readcounter fastq [OPTIONS] INPUT_FILE

    Options:
        -p, --prefix TEXT               output prefix
        -o, --output_dir TEXT           output directory  [default: ./]
        -f, --force                     force to overwrite the output file
        -l, --loglevel [critical|error|warning|info|debug]
        --version                       Show the version and exit.
        --help                          Show this message and exit.


:fastqc subcommands:

- ``readcounter fastqc``

::

    $ readcounter fastqc --help

    Usage: readcounter fastqc [OPTIONS] INPUT_FILE

    Options:
        -p, --prefix TEXT               output prefix
        -o, --output_dir TEXT           output directory  [default: ./]
        -f, --force                     force to overwrite the output file
        -l, --loglevel [critical|error|warning|info|debug]
        --version                       Show the version and exit.
        --help                          Show this message and exit.


Supported File Types
--------------------
* `fasta` format, can be compressed with zip, gzip or bzip2
* `fastq` format, can be compressed with zip, gzip or bzip2
* `fastqc` format, input must be the fastqc folder, zipped or not
* `bam` format

