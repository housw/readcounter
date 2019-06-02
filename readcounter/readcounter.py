# -*- coding: utf-8 -*-

"""Main module."""

# Copyright (C) 2018  Shengwei Hou
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from __future__ import print_function
import os
import sys
import argparse
import subprocess


class ReadCounter(object):

    _grep_map = {"none":"grep",
                "gz":"zgrep",
                "zip":"zgrep",
                "bz2":"bzgrep"
                }

    def __init__(self, input_file, format, compress_type):
        self.input_file = input_file
        self.format = format
        self.compress_type = compress_type

    def count_read_number(self):
        pass


class FastaReadCounter(ReadCounter):

    def count_read_number(self):
        grep_prog = ReadCounter._grep_map.get(self.compress_type)
        cmd = "{grep_prog} -cP '^>' {input_file}".format(grep_prog=grep_prog, input_file=self.input_file)
        return subprocess.check_output(cmd, shell=True)


class FastqReadCounter(ReadCounter):

    def count_read_number(self):
        grep_prog = ReadCounter._grep_map.get(self.compress_type)
        cmd = "{grep_prog} -cP '^@' {input_file}".format(grep_prog=grep_prog, input_file=self.input_file)
        return subprocess.check_output(cmd, shell=True)


class FastqcReadCounter(ReadCounter):

    def count_read_number(self):
        if self.compress_type == "zip":
            fastqc_zip = self.input_file
            fastqc_folder=fastqc_zip.rstrip(".zip")
            cmd = "unzip -c {fastqc_zip} {fastqc_folder}/fastqc_data.txt | grep '^Total Sequences'".format(
                fastqc_zip=fastqc_zip, fastqc_folder=fastqc_folder)
        else:
            fastqc_folder = self.input_file
            cmd = "cat {fastqc_folder}/fastqc_data.txt | grep '^Total Sequences'".format(fastqc_folder=fastqc_folder)
        line = subprocess.check_output(cmd, shell=True)
        count = line.strip().split()[-1]
        return count


class CounterDispatcher(ReadCounter):

    counter_map = {"fasta":FastaReadCounter,
                   "fastq":FastqReadCounter,
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

