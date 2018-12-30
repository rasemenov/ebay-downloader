"""
This file contains settings that user probably wants to control.
Please, be careful with formatting of this file and try to follow already set rules.
In fact this is an executable, a program to run, so special syntax applies.
"""

# Size in bytes. All images with smaller size will be skipped.
SKIP_SIZE = 2 ** 14
# File explorer will open at this directory after "Show lots" button click.
# It's vital to prepend path string with 'r'. Also take care not to end path with '\'
# To set directory with program as default simply comment whole line below with #
BASE_DIR = r'c:\Program Files\JetBrains\PyCharm Community Edition 2017.3.3\Projects\ebay_downloader'
# Everything except 'ON' will stop logging altogether
LOGGING_STATUS = 'ON'
# Control logging verbosity.
# - 'DEBUG' - write everything into log;
# - 'INFO' - somewhat less lines in log file;
# - 'ERROR' - output to log file only errors.
LOGGING_LEVEL = 'DEBUG'
