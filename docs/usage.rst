=====
Usage
=====

To use readcounter::

    $ readcounter --help
      Usage: readcounter [OPTIONS] INPUT_FILE

      count total read number in given input file.

      Options:
        -t, --format [infer|fasta|fa|fna|fastq|fq|fastqc]
                                  input file format,
                                  can be infer/fasta/fastq/fastqc  [default:
                                  infer]
        -c, --compress_type [infer|none|gz|zip|bz2]
                                  input file compress type,
                                  can be infer/none/gz/zip/bz2,
                                  it will guess gz/zip/bz2 from the suffix
                                  [default: infer]
        -p, --prefix TEXT               output prefix
        -o, --output_dir TEXT           output directory  [default: ./]
        -f, --force                     force to overwrite the output file
        --version                       Show the version and exit.
        --help                          Show this message and exit.


For example, run readcounter with a gzipped fasta input::

    $ readcounter -t fasta -c gz -o output_directory -p output_prefix input_fasta_file


Or with zipped fastqc result folder as input::

    $ readcounter -t fastqc -c zip -o output_directory -p output_prefix input_fastqc_zip_file

