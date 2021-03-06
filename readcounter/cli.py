# -*- coding: utf-8 -*-

"""Console script for readcounter."""


import os
import sys
import click
import logging
from .readcounter import CounterDispatcher
from .utils import make_output_file
from .utils import add_options
from .utils import guess_compress_type
from .utils import setup_logging


_logger = logging.getLogger(__name__)


shared_options = [
    click.argument('input_file', type=str),
    click.option('-p', '--prefix', help="output prefix", type=str), 
    click.option('-o', '--output_dir', help="output directory", default="./", show_default=True), 
    click.option('-f', '--force', is_flag=True, default=False, help="force to overwrite the output file"), 
    click.option('-l', '--loglevel', default='info', type=click.Choice(['critical', 'error', 'warning', 'info', 'debug'])),
    click.version_option(version="0.1.0", prog_name="readcounter", message="%(prog)s, version %(version)s")
]


def emit_subcommand_info(subcommand, loglevel):
    setup_logging(loglevel)
    _logger.info('invoking {0} subcommand'.format(subcommand))


@click.command()
@add_options(shared_options)
def fasta(input_file, prefix, output_dir, force, loglevel):
    emit_subcommand_info("fasta", loglevel)
    output_file = make_output_file(input_file, prefix, output_dir, force, suffix=".txt")
    compress_type = guess_compress_type(input_file)
    _logger.info('the compress type is ' + compress_type)
    # read counting
    counter = CounterDispatcher(input_file, output_file, format="fasta", compress_type=compress_type)
    counter.count_read_number()
    counter.write()


@click.command()
@add_options(shared_options)
def fastq(input_file, prefix, output_dir, force, loglevel):
    emit_subcommand_info("fastq", loglevel)
    output_file = make_output_file(input_file, prefix, output_dir, force, suffix=".txt")
    compress_type = guess_compress_type(input_file)
    _logger.info('the compress type is ' + compress_type)
    # read counting
    counter = CounterDispatcher(input_file, output_file, format="fastq", compress_type=compress_type)
    counter.count_read_number()
    counter.write()


@click.command()
@add_options(shared_options)
def fastqc(input_file, prefix, output_dir, force, loglevel):
    emit_subcommand_info("fastqc", loglevel)
    output_file = make_output_file(input_file, prefix, output_dir, force, suffix=".txt")
    compress_type = guess_compress_type(input_file)
    _logger.info('the compress type is ' + compress_type)
    # read counting
    counter = CounterDispatcher(input_file, output_file, format="fastqc", compress_type=compress_type)
    counter.count_read_number()
    counter.write()


@click.command()
@click.option('--min_read_len', help="minimum read length", type=int, default=0, show_default=True)
@click.option('--min_aln_len', help="minimum alignment length", type=int, default=0, show_default=True)
@click.option('--min_map_qual', help="minimum mapping quality", type=int, default=0, show_default=True)
@click.option('--min_base_qual', help="minimum base quality", type=int, default=0, show_default=True)
@click.option('--use_bamcov', is_flag=True, default=False, help="use bamcov for read counting", show_default=True)
@click.option('--pysam_mem', help="maximum pysam memory", type=str, default='10G', show_default=True)
@add_options(shared_options)
def bam(input_file, prefix, output_dir, force, loglevel, min_read_len, min_aln_len, min_map_qual, min_base_qual, use_bamcov, pysam_mem):
    emit_subcommand_info("bam", loglevel)
    output_file = make_output_file(input_file, prefix, output_dir, force, suffix=".txt")
    compress_type = guess_compress_type(input_file)
    _logger.info('the compress type is ' + compress_type)
    # read counting
    counter = CounterDispatcher(input_file, output_file, format="bam", compress_type=compress_type, 
    min_read_len=min_read_len, min_aln_len=min_aln_len, min_map_qual=min_map_qual, 
    min_base_qual=min_base_qual, use_bamcov=use_bamcov, pysam_mem=pysam_mem)
    counter.count_read_number()
    counter.write()


@click.group()
def main(**kwargs):
    pass

main.add_command(fasta)
main.add_command(fastq)
main.add_command(fastqc)
main.add_command(bam)


if __name__ == "__main__":
    sys.exit(main())