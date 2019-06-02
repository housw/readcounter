# -*- coding: utf-8 -*-

"""Console script for readcounter."""
import os
import sys
import click
from readcounter.readcounter import CounterDispatcher


def validate_rolls(ctx, param, value):
    try:
        rolls, dice = map(int, value.split('d', 2))
        return (dice, rolls)
    except ValueError:
        raise click.BadParameter('rolls need to be in format NdM')


@click.command()
@click.argument('input_file', type=str)
@click.option('-t', '--format', type=click.Choice(["infer", "fasta", "fastq", "fastqc"]),
                    default="infer", help="input file format, \
                         can be infer/fasta/fastq/fastqc", show_default=True)
@click.option('-c', '--compress_type', type=click.Choice(["infer", "none", "gz", "zip", "bz2"]),
                    default="infer", help="input file compress type, \
                             can be infer/none/gz/zip/bz2, \
                             it will guess gz/zip/bz2 from the suffix", show_default=True)
@click.option('-p', '--prefix', help="output prefix", type=str)
@click.option('-o', '--output_dir', help="output directory", default="./", show_default=True)
@click.option('-f', '--force', is_flag=True, help="force to overwrite the output file")
@click.version_option(version="0.1.0", prog_name="%(prog)", message="%(prog)s, version %(version)s")
def main(input_file, format, compress_type, prefix, output_dir, force):
    """count total read number in given input file."""

    suffix = input_file.split(".")[-1]

    # compress_type handeling
    compress_map = { "gz": "gz", "gzip":"gz",
                     "bz2": "bz2", "bzip2": "bz2",
                     "zip": "zip"}
    if compress_type == "infer":
        if suffix in compress_map:
            compress_type = compress_map.get(suffix)
        else:
            compress_type = "none"

    # input file format handeling
    format_map = { "fa": "fasta", "fas": "fasta", "fasta": "fasta", "fna": "fasta", "faa": "fasta",
                   "fq": "fastq", "fastq": "fastq",
                   "fastqc": "fastqc"}
    if format == "infer":
        if "fastqc" in input_file:
            suffix = "fastqc"
        elif suffix in compress_map:
            if len(input_file.split(".")) > 2:
                suffix = input_file.split(".")[-2]
            else:
                err_msg="\nERROR: {suffix} file format is not supported!\n".format(suffix=suffix)
                raise click.UsageError(message=err_msg)
        if suffix in format_map:
            format = format_map.get(suffix)
        else:
            err_msg = "\nERROR: {suffix} file format is not supported!\n".format(suffix=suffix)
            raise click.UsageError(message=err_msg)

    # input and output handeling
    if not prefix:
        basename = os.path.basename(input_file)
        prefix = os.path.splitext(basename)[0]
        out_file = os.path.join(output_dir, prefix + "_read_number.txt")

    if os.path.exists(out_file):
        if force:
            click.echo("Warning: output file exists, will be overwriten!")
        else:
            err_msg = "output file detected, please backup it at first!"
            raise click.UsageError(message=err_msg)

    with open(out_file, "w") as oh:
        counter = CounterDispatcher(input_file, format, compress_type)
        counter.count_read_number()
        oh.write(str(counter) + '\n')

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover


