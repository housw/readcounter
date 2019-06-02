# -*- coding: utf-8 -*-

"""Main module."""


from __future__ import print_function
import os
import sys
import argparse
import subprocess
import logging


class ReadCounter(object):
    """Abstract ReadCounter class.

    Note:
        Do not initialize this abstract class, inherit and implement the `count_read_number` method.

    Attributes:
        input_file (str): input file to count read number.
        format (str): file format, i.e., `fastq`, `fasta`, etc.
        compress_type (str): compress suffix, i.e., `zip`, `bz2`, `gz`, etc.
    """

    _grep_map = {"none":"grep",
                "gz":"zgrep",
                "zip":"zgrep",
                "bz2":"bzgrep"
                }

    def __init__(self, input_file, format, compress_type):
        """ To initialize a ReadCounter object

        Args:
            input_file (str): input file for read counting
            format (str): input file format
            compress_type (str): type of compression
        """

        self.input_file = input_file
        self.format = format
        self.compress_type = compress_type

    def count_read_number(self):
        pass


class FastaReadCounter(ReadCounter):

    def count_read_number(self):
        """This function implement read counting for input files in fasta format."""

        grep_prog = ReadCounter._grep_map.get(self.compress_type)
        cmd = "{grep_prog} -c '^>' {input_file}".format(grep_prog=grep_prog, input_file=self.input_file)
        return subprocess.check_output(cmd, shell=True)


class FastqReadCounter(ReadCounter):

    def count_read_number(self):
        """This function implement read counting for input files in fastq format."""

        grep_prog = ReadCounter._grep_map.get(self.compress_type)
        cmd = "{grep_prog} -c '^@' {input_file}".format(grep_prog=grep_prog, input_file=self.input_file)
        return subprocess.check_output(cmd, shell=True)


class FastqcReadCounter(ReadCounter):

    def count_read_number(self):
        """This function implement read counting for input files in fastqc format."""

        if self.compress_type == "zip":
            fastqc_zip = self.input_file
            abs_path = os.path.abspath(fastqc_zip)
            base_name = os.path.basename(abs_path).rstrip('.zip')
            dir_name = os.path.dirname(abs_path)
            fastqc_folder = dir_name + "/" + base_name
            cmd = "unzip -o {fastqc_zip} -d {dir_name} && cat {fastqc_folder}/fastqc_data.txt | " \
                  "grep '^Total Sequences'".format(fastqc_zip=fastqc_zip, dir_name=dir_name, fastqc_folder=fastqc_folder)
        else:
            fastqc_folder = self.input_file
            cmd = "cat {fastqc_folder}/fastqc_data.txt | grep '^Total Sequences'".format(fastqc_folder=fastqc_folder)
        line = subprocess.check_output(cmd, shell=True)
        count = line.strip().split()[-1]
        return count


class CounterDispatcher(ReadCounter):
    """dispatch read counting jobs"""

    counter_map = {"fasta":FastaReadCounter,
                   "fa":FastaReadCounter,
                   "fna":FastaReadCounter,
                   "fastq":FastqReadCounter,
                   "fq":FastqReadCounter,
                   "fastqc":FastqcReadCounter
                   }

    def __init__(self, input_file, format, compress_type):
        try:
            super().__init__(input_file, format, compress_type)
        except Exception as e:
            print("WARNING: Python3 is not supported by your interpreter: {err_msg}, using Python2 instead".format(err_msg=e))
            super(CounterDispatcher, self).__init__(input_file, format, compress_type)
        self.counter = self._get_read_counter()
        self.read_count = 0

    def _get_read_counter(self):
        return CounterDispatcher.counter_map.get(self.format, None)

    def count_read_number(self):
        counter = self.counter(self.input_file, self.format, self.compress_type)
        self.read_count = counter.count_read_number()

    def __str__(self):
        _basename = os.path.basename(self.input_file)
        _filestem = os.path.splitext(_basename)[0]
        return "{filestem} : {read_count:d}".format(filestem=_filestem, read_count=int(self.read_count))
