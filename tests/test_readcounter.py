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
        return pkg_resources.resource_filename(__name__, 'test_data/test.{suffix}'.format(suffix=format))
    else:
        if format != 'fq':
            raise cli.UsageError(message="only compressed fq files are available in the test folder!")
        return pkg_resources.resource_filename(__name__, 'test_data/test.{suffix}.{compress}'.format(suffix=format, compress=compress_type))

def get_test_result_file(runner, format='fa', compress_type='none'):
    input_file = get_test_input_file(format=format)
    format = format
    output_dir = "./tests/test_results"
    output_prefix = "test_{s}".format(s=format)
    result = runner.invoke(cli.main, ['--format', format, 
                                      '--output_dir', output_dir, 
                                      '--prefix', output_prefix,
                                      '--compress_type', compress_type,
                                      '--force', input_file])
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0
    output_file = os.path.join(output_dir, output_prefix + "_read_number.txt")
    return output_file


def test_help(runner):
    """Test readcounter --help"""
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help                          Show this message and exit.' \
        in help_result.output


def test_version(runner):
    """Test readcounter --version"""
    help_result = runner.invoke(cli.main, ['--version'])
    assert help_result.exit_code == 0
    assert 'readcounter, version {v}'.format(v=version) \
        in help_result.output


def test_input_fa(runner):
    output_file = get_test_result_file(runner, format='fa')
    read_count = open(output_file, 'r').read()
    assert read_count == 'test : 250\n'


def test_input_fna(runner):
    output_file = get_test_result_file(runner, format='fna')
    read_count = open(output_file, 'r').read()
    assert read_count == 'test : 250\n'


def test_input_fasta(runner):
    output_file = get_test_result_file(runner, format='fasta')
    read_count = open(output_file, 'r').read()
    assert read_count == 'test : 250\n'


def test_input_fastq(runner):
    output_file = get_test_result_file(runner, format='fastq')
    read_count = open(output_file, 'r').read()
    assert read_count == 'test : 250\n'


def test_input_fq(runner):
    output_file = get_test_result_file(runner, format='fq')
    read_count = open(output_file, 'r').read()
    assert read_count == 'test : 250\n'


def test_input_fq_gz(runner):
    output_file = get_test_result_file(runner, format='fq', compress_type='gz')
    read_count = open(output_file, 'r').read()
    assert read_count == 'test : 250\n'


def test_input_fq_bz2(runner):
    output_file = get_test_result_file(runner, format='fq', compress_type='bz2')
    read_count = open(output_file, 'r').read()
    assert read_count == 'test : 250\n'


def test_input_fq_zip(runner):
    output_file = get_test_result_file(runner, format='fq', compress_type='zip')
    read_count = open(output_file, 'r').read()
    assert read_count == 'test : 250\n'


def test_input_fastqc_zip(runner):
    input_file = pkg_resources.resource_filename(__name__, 'test_data/sample1_fastqc.zip')    
    format = 'fastqc'
    output_dir = "./tests/test_results"
    output_prefix = "test_{s}_zip".format(s=format)
    result = runner.invoke(cli.main, ['--format', format, 
                                      '--output_dir', output_dir, 
                                      '--prefix', output_prefix,
                                      '--compress_type', 'zip',
                                      '--force', input_file])
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0
    output_file = os.path.join(output_dir, output_prefix + "_read_number.txt")
    read_count = open(output_file, 'r').read()
    assert read_count == 'sample1_fastqc : 12733986\n'


def test_input_fastqc_folder(runner):
    input_file = pkg_resources.resource_filename(__name__, 'test_data/sample2_fastqc')
    format = 'fastqc'
    output_dir = "./tests/test_results"
    output_prefix = "test_{s}".format(s=format)
    result = runner.invoke(cli.main, ['--format', format,
                                      '--output_dir', output_dir,
                                      '--prefix', output_prefix,
                                      '--compress_type', 'none',
                                      '--force', input_file])
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0
    output_file = os.path.join(output_dir, output_prefix + "_read_number.txt")
    read_count = open(output_file, 'r').read()
    assert read_count == 'sample2_fastqc : 12733986\n'


def test_input_bam_file(runner):
    input_file = pkg_resources.resource_filename(__name__, 'test_data/test.bam')
    input_count_file = pkg_resources.resource_filename(__name__, 'test_data/bam_read_number.txt')
    format = 'bam'
    output_dir = "./tests/test_results"
    output_prefix = "test_{s}".format(s=format)
    result = runner.invoke(cli.main, ['--format', format,
                                      '--output_dir', output_dir,
                                      '--prefix', output_prefix,
                                      '--compress_type', 'none',
                                      '--force', input_file])
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0
    output_file = os.path.join(output_dir, output_prefix + "_read_number.txt")
    read_count = open(output_file, 'r').read()
    ret_code = subprocess.check_call("diff {in_count} {out_count}".format(in_count=input_count_file, out_count=output_file), shell=True)
    assert ret_code == 0
