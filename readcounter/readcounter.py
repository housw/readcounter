# -*- coding: utf-8 -*-

"""Main module."""


from __future__ import print_function
import os
import sys
import argparse
import subprocess
import logging
import shutil
import tempfile
import pysam


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

    def __str__(self):
        _basename = os.path.basename(self.input_file)
        _filestem = os.path.splitext(_basename)[0]
        return "{filestem} : {read_count:d}".format(filestem=_filestem, read_count=int(self.read_count))


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
        count = line.strip().split()[-1]
        for folder in cleanup_folder:
            try:
                shutil.rmtree(folder, ignore_errors=False)
            except Exception as e:
                print(e)
        return count


class BamReadCounter(ReadCounter):

    def __init__(self, input_file, format="bam", compress_type="none"):
        try:
            super().__init__(input_file, format, compress_type)
        except Exception as e:
            print("WARNING: Python3 is not supported by your interpreter: {err_msg}, using Python2 instead".format(err_msg=e))
            super(BamReadCounter, self).__init__(input_file, format, compress_type)
        self.read_count = 0

    def _get_depth_per_bam_file(self, min_read_len=30, min_MQ=0, min_BQ=0, pysam_mem='10G'):

        # create tmp dir and file to save bamcov result
        input_basename = os.path.basename(self.input_file)
        input_filestem = os.path.splitext(input_basename)[0]
        tmp_bamcov_dir = tempfile.mkdtemp()
        tmp_bamcov_file = os.path.join(tmp_bamcov_dir, input_filestem+"_bamcov.tsv")
        print(tmp_bamcov_dir, tmp_bamcov_file)

        if not os.path.exists(self.input_file + ".bai"):
            pysam.index(self.input_file)

        # command for bamcov
        cmd = ['bamcov', '--output', tmp_bamcov_file,
               '--min-read-len', str(min_read_len),
               '--min-MQ', str(min_MQ),
               '--min-BQ', str(min_BQ),
               self.input_file]
        print("[bamcov] {c}".format(c=" ".join(cmd)))
        try:
            ret_code = subprocess.check_call(cmd, shell=False)
        except Exception as e:
            print("It seems like your bam file is not sorted, trying to sort it and run bamcov again ...")
            try:
                tmp_file = tempfile.mkstemp()[1]
                print(tmp_file)
                pysam.sort("-o", tmp_file, self.input_file)
                shutil.move(tmp_file, self.input_file)
                pysam.index(self.input_file)
                ret_code = subprocess.check_call(cmd, shell=False)
            except Exception as e:
                raise Exception("failed to call bamcov, try to debug in terminal with this command {cmd}".format(cmd=" ".join(cmd)))

        return tmp_bamcov_file


    def count_read_number(self):
        """This function implement read counting for input files in bam format."""

        bamcov_file = self._get_depth_per_bam_file()
        '''
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
        count = line.strip().split()[-1]
        for folder in cleanup_folder:
            try:
                shutil.rmtree(folder, ignore_errors=False)
            except Exception as e:
                print(e)
        return count
        '''





    """
    def calculate_contig_depth_from_bam_files(input_bam_file_list, output_dir, output_prefix):
    
        depth_files = []
        sample_names = []
    
        # run bamcov for each bam file
        for bam_file in input_bam_file_list:
            basename = os.path.basename(bam_file)
            filestem = os.path.splitext(basename)[0]
            depth_file = os.path.join(output_dir, filestem+"_bamcov.tsv")
            get_depth_per_bam_file(bam_file, depth_file)
            sample_names.append(filestem)
            depth_files.append(depth_file)
    
        # write contig length file
        output_length_file = os.path.join(output_dir, output_prefix+"_length.tsv")
        first_df = pd.read_csv(depth_files[0], sep='\t', header=0, index_col=0)
        length_df = first_df[['endpos']]
        length_df.rename(columns={'endpos':'Length'}, inplace=True)
        length_df.index.name = "Contig_ID"
        length_df.to_csv(output_length_file, sep='\t', header=True, index=True)
    
        # merge depth profiles and write depth file
        output_depth_file = os.path.join(output_dir, output_prefix+"_depth.tsv")
        all_depth_dfs = []
        shape = None
        for i, depth_file in enumerate(depth_files):
            curr_depth_df = pd.read_csv(depth_file, sep='\t', header=0, index_col=0).meandepth.rename(sample_names[i])
            if not shape:
                shape = curr_depth_df.shape
            else:
                assert curr_depth_df.shape == shape, "input depth files has different dimensions!"
            all_depth_dfs.append(curr_depth_df)
        depth_df = pd.concat(all_depth_dfs, axis=1)
        depth_df.index.name="Contig_ID"
        depth_df.to_csv(output_depth_file, sep="\t", header=True, index=True)
    """















class CounterDispatcher(ReadCounter):
    """dispatch read counting jobs"""

    counter_map = {"fasta": FastaReadCounter,
                   "fa": FastaReadCounter,
                   "fna": FastaReadCounter,
                   "fastq": FastqReadCounter,
                   "fq": FastqReadCounter,
                   "fastqc": FastqcReadCounter,
                   "bam": BamReadCounter
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

