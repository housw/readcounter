# -*- coding: utf-8 -*-


import os
import sys
import click
import logging


_logger = logging.getLogger(__name__)


# credit: https://github.com/pallets/click/issues/108
def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options


def make_output_file(input_file, prefix=None, output_dir="./", force=False, suffix=".txt"):
    """make output_file, check existence"""

    # input and output handeling
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not prefix:
        basename = os.path.basename(os.path.normpath(input_file))
        _logger.debug("output basename is {}".format(basename))
        if "." in basename:
            prefix, ext = os.path.splitext(basename)
        else:
            prefix, ext = basename, "None"
        # e.g., remove .fq.gz
        if ext in (".gz", ".gzip", ".bz2", ".bzip2", ".zip"):
            prefix = os.path.splitext(prefix)[0]
    _logger.info("output prefix is {}".format(prefix))
    out_file = os.path.join(output_dir, prefix + suffix)
    _logger.info("output file is {}".format(out_file))
    if os.path.exists(out_file):
        if force:
            _logger.warning("output file exists, will be overwritten!")
        else:
            err_msg = "output file detected, please backup it at first!\n\n"
            _logger.error(err_msg)
            raise click.UsageError(message=err_msg)
    return out_file


def guess_compress_type(input_file):
    """ guess compression type """

    # compress_type handeling
    compress_map = { "gz": "gz", "gzip":"gz",
                     "bz2": "bz2", "bzip2": "bz2",
                     "zip": "zip"}

    suffix = input_file.split(".")[-1]
    if suffix in compress_map:
        compress_type = compress_map.get(suffix)
    else:
        compress_type = "none"
    
    return compress_type


def setup_logging(loglevel):
    """Setup basic loggings
    Args:
      loglevel (str): minimum loglevel for emitting messages
    """

    loglevel = {
        'critical': logging.CRITICAL,
        'error'   : logging.ERROR,
        'warning' : logging.WARNING,
        'info'    : logging.INFO,
        'debug'   : logging.DEBUG,
    }.get(loglevel, logging.DEBUG)

    logformat = "[%(asctime)s] [%(levelname)s] %(name)s:%(message)s"

    logging.basicConfig(level=loglevel, format=logformat, datefmt="%Y-%m-%d %H:%M:%S")