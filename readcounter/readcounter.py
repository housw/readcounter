# -*- coding: utf-8 -*-

"""Main module."""


from __future__ import print_function
import os
import sys
import argparse
import logging
import shutil
import tempfile
import pysam
import numpy as np
import pandas as pd
import subprocess
from subprocess import Popen, PIPE
from abc import ABC, abstractmethod


_logger = logging.getLogger(__name__)


class ReadCounter(ABC):
    """Abstract ReadCounter class.

    Note:
        Do not initialize this abstract class,
        instead, please inherit this abstract class and implement the `count_read_number` and `write` abstract methods.

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

    def __init__(self, input_file, out_file, compress_type, *args, **kwargs):
        """ To initialize a ReadCounter object

        Args:
            input_file (str): input file for read counting
            format (str): input file format
            compress_type (str): type of compression
        """

        self.input_file = input_file
        self.out_file = out_file
        self.compress_type = compress_type
        self.read_count = 0

    @property
    def output_filestem(self):
        # use normpath to catch basename for fastqc folder
        _base_name = os.path.basename(os.path.normpath(self.input_file))
        if "." in _base_name:
            _file_stem, ext = os.path.splitext(_base_name)
        else:
            _file_stem, ext = _base_name, "None"
        # e.g., remove .fq.gz
        if ext in (".gz", ".gzip", ".bz2", ".bzip2", ".zip"):
            _file_stem = os.path.splitext(_file_stem)[0]
        return _file_stem

    @abstractmethod
    def count_read_number(self):
        pass

    @abstractmethod
    def write(self):
        pass


class FastaReadCounter(ReadCounter):

    def count_read_number(self):
        """This function implement read counting for input files in fasta format."""

        grep_prog = ReadCounter._grep_map.get(self.compress_type)
        cmd = "{grep_prog} -c '^>' {input_file}".format(grep_prog=grep_prog, input_file=self.input_file)
        p = subprocess.Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        read_count, err = p.communicate()
        self.read_count = read_count.strip()

    def write(self):
        with open(self.out_file, 'w') as oh:
            oh.write("{filestem} : {read_count:d}".format(filestem=self.output_filestem, read_count=int(self.read_count)) + "\n")


class FastqReadCounter(ReadCounter):

    def count_read_number(self):
        """This function implement read counting for input files in fastq format."""

        grep_prog = ReadCounter._grep_map.get(self.compress_type)
        cmd = "{grep_prog} -c '^@' {input_file}".format(grep_prog=grep_prog, input_file=self.input_file)
        p = subprocess.Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        read_count, err = p.communicate()
        self.read_count = read_count.strip()

    def write(self):
        with open(self.out_file, 'w') as oh:
            oh.write("{filestem} : {read_count:d}".format(filestem=self.output_filestem, read_count=int(self.read_count)) + "\n")


class FastqcReadCounter(ReadCounter):

    def count_read_number(self):
        """This function implement read counting for input files in fastqc format."""

        cleanup_folder = []
        if self.compress_type == "zip":
            fastqc_zip = self.input_file
            abs_path = os.path.abspath(fastqc_zip)
            base_name = os.path.basename(abs_path).rstrip('.zip')
            dir_name = os.path.dirname(abs_path)
            fastqc_folder = dir_name + "/" + base_name
            cmd = "unzip -o {fastqc_zip} -d {dir_name} && cat {fastqc_folder}/fastqc_data.txt | " \
                  "grep '^Total Sequences'".format(fastqc_zip=fastqc_zip, dir_name=dir_name, fastqc_folder=fastqc_folder)
            cleanup_folder.append(fastqc_folder)
        else:
            fastqc_folder = self.input_file
            cmd = "cat {fastqc_folder}/fastqc_data.txt | grep '^Total Sequences'".format(fastqc_folder=fastqc_folder)
        line = subprocess.check_output(cmd, shell=True)
        read_count = line.strip().split()[-1]
        for folder in cleanup_folder:
            try:
                shutil.rmtree(folder, ignore_errors=False)
            except Exception as e:
                _logger.warning(e)
        self.read_count = read_count

    def write(self):
        with open(self.out_file, 'w') as oh:
            oh.write("{filestem} : {read_count:d}".format(filestem=self.output_filestem, read_count=int(self.read_count)) + "\n")


class BamReadCounter(ReadCounter):

    def __init__(self, input_file, out_file, compress_type="none", min_read_len=0, min_aln_len=0, min_map_qual=0, min_base_qual=0, use_bamcov=False, pysam_mem='10G'):
        try:
            super().__init__(input_file, out_file, compress_type)
        except Exception as e:
            _logger.warning("Python3 is not supported by your interpreter: {err_msg}, using Python2 instead".format(err_msg=e))
            super(BamReadCounter, self).__init__(input_file, out_file, compress_type)
        self.min_read_len = min_read_len
        self.min_aln_len = min_aln_len
        self.min_map_qual = min_map_qual
        self.min_base_qual = min_base_qual
        self.use_bamcov = use_bamcov

    def _get_depth_per_bam_file_via_bamcov(self):

        # create tmp dir and file to save bamcov result
        input_basename = os.path.basename(self.input_file)
        input_filestem = os.path.splitext(input_basename)[0]
        tmp_bamcov_dir = tempfile.mkdtemp()
        tmp_bamcov_file = os.path.join(tmp_bamcov_dir, input_filestem+"_bamcov.tsv")

        if not os.path.exists(self.input_file + ".bai"):
            _logger.info("indexing input bam file")
            pysam.index(self.input_file)

        _logger.info("min_read_len is: "+ str(self.min_read_len))
        # command for bamcov
        cmd = ['bamcov', '--output', tmp_bamcov_file,
               '--min-read-len', str(self.min_read_len),
               '--min-MQ', str(self.min_map_qual),
               '--min-BQ', str(self.min_base_qual),
               self.input_file]
        _logger.info("counting mapped reads using bamcov")
        _logger.info("[bamcov commandline] {c}".format(c=" ".join(cmd)))
        try:
            p = subprocess.Popen(cmd, shell=False, stdout=PIPE, stderr=PIPE)
            output, err = p.communicate()
        except Exception as e:
            _logger.warning("It seems like your bam file is not sorted, trying to sort it and run bamcov again ...")
            try:
                tmp_file = tempfile.mkstemp()[1]
                _logger.debug(tmp_file)
                pysam.sort("-o", tmp_file, self.input_file)
                shutil.move(tmp_file, self.input_file)
                pysam.index(self.input_file)
                ret_code = subprocess.check_call(cmd, shell=False)
            except Exception as e:
                raise Exception("failed to call bamcov, try to debug in terminal with this command {cmd}".format(cmd=" ".join(cmd)))

        # return bamcov df
        df = pd.read_csv(tmp_bamcov_file, sep='\t')
        shutil.rmtree(tmp_bamcov_dir, ignore_errors=True)
        return df

    def _get_depth_per_bam_file(self):
        """ get read count for each contig"""

        def filter_read(aln):
            # possible filters
            # aln.is_paired=True
            # np.mean(aln.query_alignment_qualities[1])=30
            if ((not aln.is_unmapped) and (not aln.is_duplicate) and (not aln.is_qcfail) and 
                (not aln.is_secondary) and 
                (not aln.is_supplementary) and 
                (aln.query_length >= self.min_read_len) and 
                (aln.mapping_quality >= self.min_map_qual) and 
                (np.mean(aln.query_qualities[1]) >= self.min_base_qual) and 
                (aln.query_alignment_length >= self.min_aln_len)):
                return True
            else:
                return False

        # create tmp dir and file to save bamcov result
        input_basename = os.path.basename(self.input_file)
        input_filestem = os.path.splitext(input_basename)[0]
  
        if not os.path.exists(self.input_file + ".bai"):
            _logger.info("indexing input bam file")
            pysam.index(self.input_file)

        samfile = pysam.AlignmentFile(self.input_file, "rb") 
        df = pd.DataFrame(samfile.header['SQ'])
        df['start'] = [0]*len(df.index)
        df['numreads'] = 0*len(df.index)
        df.columns = ['endpos', '#rname', 'start', 'numreads']

        _logger.info("counting mapped reads using pysam")
        for i in df.index: 
            stop, contig, start, numreads = df.loc[i,] 
            count = samfile.count(contig=contig, start=start, stop=stop, region=None, until_eof=False, read_callback=filter_read)
            df.loc[i, 'numreads'] = count 
        
        return df

    def count_read_number(self):
        """This function implement read counting for input files in bam format."""
        if self.use_bamcov:
            try: 
                df = self._get_depth_per_bam_file_via_bamcov()
            except Exception as e:
                _logger.error("it seems bamcov doesn't work for you, use pysam instead")
                df = self._get_depth_per_bam_file()
        else:
            df = self._get_depth_per_bam_file()
        selected_df = df[['#rname', 'endpos', 'numreads']] #, 'covbases', 'coverage', 'meandepth']]
        selected_df.columns = ['contig', 'length', 'numreads']
        selected_df = selected_df[selected_df['numreads'] != 0]
        self.read_count = selected_df

    def write(self):
        self.read_count.to_csv(path_or_buf=self.out_file, sep='\t', header=True, index=False)


class CounterDispatcher(ReadCounter):
    """dispatch read counting jobs"""

    counter_map = {"fasta": FastaReadCounter,
                   "fastq": FastqReadCounter,
                   "fastqc": FastqcReadCounter,
                   "bam": BamReadCounter, 
                   "sam": BamReadCounter
                   }

    def __init__(self, input_file, out_file, format, compress_type, *args, **kwargs):
        try:
            super().__init__(input_file, out_file, compress_type, *args, **kwargs)
        except Exception as e:
            _logger.warning("Python3 is not supported by your interpreter: {err_msg}, using Python2 instead".format(err_msg=e))
            super(CounterDispatcher, self).__init__(input_file, out_file, compress_type, *args, **kwargs)
        self.format = format
        # get corresponding Counter class, and initialize a readcounter object
        _Counter = CounterDispatcher.counter_map.get(self.format, None)
        self.counter = _Counter(self.input_file, self.out_file, self.compress_type, *args, **kwargs)

    def count_read_number(self):
        self.counter.count_read_number()

    def write(self):
        self.counter.write()