#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `readcounter` package."""
import os
import pytest
import traceback
import subprocess
from click.testing import CliRunner
from readcounter import readcounter
from readcounter import cli
from readcounter import __version__ as version
import pkgutil
import pkg_resources


@pytest.fixture(scope="module")
def runner():
    return CliRunner()


def get_test_input_file(format='fq', compress_type='none'):
    if compress_type == 'none':
        input_file = pkg_resources.resource_filename(__name__, 'test_data/test.{suffix}'.format(suffix=format))
    else:
        if format not in ('fasta', 'fq', 'fastq','sam', 'bam', 'fastqc'):
            raise cli.UsageError(message="only compressed fq files are available in the test folder!")
        input_file = pkg_resources.resource_filename(__name__, 'test_data/test.{suffix}.{compress}'.format(suffix=format, compress=compress_type))
    return input_file


def test_help(runner):
    """Test readcounter --help"""
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert 'Show this message and exit.' \
        in help_result.output


def test_version(runner):
    """Test readcounter --version"""
    version_result = runner.invoke(cli.main, ['fasta', '--version'])
    assert version_result.exit_code == 0
    assert 'readcounter, version {v}'.format(v=version) \
        in version_result.output


def test_plain_fasta_input(runner):
    input_file = get_test_input_file(format="fasta")
    output_dir = "./tests/test_results"
    output_prefix = "test_plain_fasta"
    result = runner.invoke(cli.main, ['fasta', 
                                      '--output_dir', output_dir, 
                                      '--prefix', output_prefix,
                                      '--force', input_file])
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0
    output_file = os.path.join(output_dir, output_prefix + ".txt")
    read_count = open(output_file, 'r').read()
    assert read_count == 'test : 250\n'


def test_gzip_fasta_input(runner):
    input_file = get_test_input_file(format="fasta", compress_type='gz')
    output_dir = "./tests/test_results"
    output_prefix = "test_gzip_fasta"
    result = runner.invoke(cli.main, ['fasta', 
                                      '--output_dir', output_dir, 
                                      '--prefix', output_prefix,
                                      '--force', input_file])
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0
    output_file = os.path.join(output_dir, output_prefix + ".txt")
    read_count = open(output_file, 'r').read()
    assert read_count == 'test : 250\n'


def test_plain_fastq_input(runner):
    input_file = get_test_input_file(format="fastq")
    output_dir = "./tests/test_results"
    output_prefix = "test_plain_fasta"
    result = runner.invoke(cli.main, ['fastq', 
                                      '--output_dir', output_dir, 
                                      '--prefix', output_prefix,
                                      '--force', input_file])
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0
    output_file = os.path.join(output_dir, output_prefix + ".txt")
    read_count = open(output_file, 'r').read()
    assert read_count == 'test : 250\n'


def test_gz_fq(runner):
    input_file = get_test_input_file(format='fq', compress_type='gz')
    output_dir = "./tests/test_results"
    output_prefix = "test_gz_fastq"
    result = runner.invoke(cli.main, ['fastq', 
                                      '--output_dir', output_dir, 
                                      '--prefix', output_prefix,
                                      '--force', input_file])
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0
    output_file = os.path.join(output_dir, output_prefix + ".txt")
    read_count = open(output_file, 'r').read()
    assert read_count == 'test : 250\n'


def test_bz2_fq(runner):
    input_file = get_test_input_file(format='fq', compress_type='bz2')
    output_dir = "./tests/test_results"
    output_prefix = "test_bz2_fastq"
    result = runner.invoke(cli.main, ['fastq', 
                                      '--output_dir', output_dir, 
                                      '--prefix', output_prefix,
                                      '--force', input_file])
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0
    output_file = os.path.join(output_dir, output_prefix + ".txt")
    read_count = open(output_file, 'r').read()
    assert read_count == 'test : 250\n'


def test_zip_fq(runner):
    input_file = get_test_input_file(format='fq', compress_type='zip')
    output_dir = "./tests/test_results"
    output_prefix = "test_zip_fastq"
    result = runner.invoke(cli.main, ['fastq', 
                                      '--output_dir', output_dir, 
                                      '--prefix', output_prefix,
                                      '--force', input_file])
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0
    output_file = os.path.join(output_dir, output_prefix + ".txt")
    read_count = open(output_file, 'r').read()
    assert read_count == 'test : 250\n'


def test_input_fastqc_folder(runner):
    input_file = pkg_resources.resource_filename(__name__, 'test_data/sample2_fastqc')
    output_dir = "./tests/test_results"
    output_prefix = "test_input_fastqc_folder"
    result = runner.invoke(cli.main, ['fastqc',
                                      '--output_dir', output_dir,
                                      '--prefix', output_prefix,
                                      '--force', input_file])
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0
    output_file = os.path.join(output_dir, output_prefix + ".txt")
    read_count = open(output_file, 'r').read()
    assert read_count == 'sample2_fastqc : 12733986\n'


def test_input_fastqc_zip(runner):
    input_file = pkg_resources.resource_filename(__name__, 'test_data/sample1_fastqc.zip')    
    output_dir = "./tests/test_results"
    output_prefix = "test_input_fastqc_zip"
    result = runner.invoke(cli.main, ['fastqc', 
                                      '--output_dir', output_dir, 
                                      '--prefix', output_prefix,
                                      '--force', input_file])
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0
    output_file = os.path.join(output_dir, output_prefix + ".txt")
    read_count = open(output_file, 'r').read()
    assert read_count == 'sample1_fastqc : 12733986\n'



def test_input_bam_file(runner):
    input_file = pkg_resources.resource_filename(__name__, 'test_data/test.bam')
    input_count_file = pkg_resources.resource_filename(__name__, 'test_data/bam_read_number.txt')
    output_dir = "./tests/test_results"
    output_prefix = "test_input_bam_file"
    result = runner.invoke(cli.main, ['bam', 
                                      '--output_dir', output_dir,
                                      '--prefix', output_prefix,
                                      '--force', input_file])
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0
    output_file = os.path.join(output_dir, output_prefix + ".txt")
    read_count = open(output_file, 'r').read()
    ret_code = subprocess.check_call("diff {in_count} {out_count}".format(in_count=input_count_file, out_count=output_file), shell=True)
    assert ret_code == 0
