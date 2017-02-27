#!/usr/bin/env python
"""
NAME
    clean_filenames.py - short description

SYNOPSIS
    Put synposis here.

DESCRIPTION
    Put description here.

OPTIONS
    -h, --help
        Prints this manual and exits.
        
    -n VAL
        Blah blah.

AUTHOR
    Ryan Reece  <ryan.reece@cern.ch>

COPYRIGHT
    Copyright 2010 Ryan Reece
    License: GPL <http://www.gnu.org/licenses/gpl.html>

SEE ALSO
    ROOT <http://root.cern.ch>

TO DO
    - One.
    - Two.

2011-06-15
"""

#------------------------------------------------------------------------------
# imports
#------------------------------------------------------------------------------

## std
import argparse, sys, time
import glob
import os
import re
import subprocess
import unicodedata

## others
#from PyPDF2 import PdfFileReader

## my modules

## local modules



#------------------------------------------------------------------------------
# globals
#------------------------------------------------------------------------------
timestamp = time.strftime('%Y-%m-%d-%Hh%M')


#------------------------------------------------------------------------------
# options
#------------------------------------------------------------------------------
def options():
    parser = argparse.ArgumentParser()
    parser.add_argument('infiles', nargs='+', default=None,
            help='A positional argument.')
    parser.add_argument('-x', '--option',  default=False,  action='store_true',
            help="Some toggle option.")
    return parser.parse_args()


#------------------------------------------------------------------------------
# main
#------------------------------------------------------------------------------
def main():
    ops = options()

    infiles = ops.infiles
    assert infiles

    n_renamed = 0

    for fn in infiles:

#        print '  Cleaning file: %s' % fn
        new_fn = clean_filename(fn)
        if fn != new_fn:
            rename(fn, new_fn)
            n_renamed += 1

    print ''
    print '  %i files renamed:' % n_renamed
    print ''


#------------------------------------------------------------------------------
# free functions
#------------------------------------------------------------------------------

#______________________________________________________________________________
def clean_filename(fn):
    new_fn = str(fn)

    # split name, ext
    new_fn, ext = os.path.splitext(new_fn)

    ## remove extra spaces and convert to '-'
    new_fn = new_fn.strip()
    u_new_fn = unicode(new_fn, 'utf-8')

    ## change unicode-hyphen-like characters to ascii
    u_new_fn = u_new_fn.replace(u'\u2010', '-')
    u_new_fn = u_new_fn.replace(u'\u2011', '-')
    u_new_fn = u_new_fn.replace(u'\u2012', '-')
    u_new_fn = u_new_fn.replace(u'\u2013', '-')
    u_new_fn = u_new_fn.replace(u'\u2014', '-')
    u_new_fn = u_new_fn.replace(u'\u2015', '-')

    ## convert unicode to closest ascii for latin-like characters
    ## punctuation-like characters not switched to ascii above will be lost
    ## help from: http://stackoverflow.com/questions/1207457/convert-a-unicode-string-to-a-string-in-python-containing-extra-symbols
    u_new_fn = unicodedata.normalize('NFKD', u_new_fn)
    u_new_fn = u_new_fn.encode('ascii','ignore')
    new_fn = str(u_new_fn)

    ## change . to -
    new_fn = new_fn.replace('.', '-')

    ## remove redundant space
    new_fn = new_fn.replace('     ', ' ')
    new_fn = new_fn.replace('    ', ' ')
    new_fn = new_fn.replace('   ', ' ')
    new_fn = new_fn.replace('  ', ' ')
    new_fn = new_fn.replace(' ', '-')
    new_fn = new_fn.replace('_____', ' ')
    new_fn = new_fn.replace('____', ' ')
    new_fn = new_fn.replace('___', ' ')
    new_fn = new_fn.replace('__', ' ')
    new_fn = new_fn.replace('_', '-')
    new_fn = new_fn.replace('-----', '-')
    new_fn = new_fn.replace('----', '-')
    new_fn = new_fn.replace('---', '-')
    new_fn = new_fn.replace('--', '-')
#    new_fn = new_fn.replace('.-', '.')
#    new_fn = new_fn.replace('-.', '.')

    ## remove strange characters
    len_fn = len(new_fn)
    i = 0
    while i < len_fn:
        ch = new_fn[i]
        if not re.match(r'[a-zA-Z0-9_.\-]', ch): # \w = [a-zA-Z0-9_]
            new_fn = new_fn.replace(ch, '_')
            len_fn = len(new_fn)
        i += 1
    new_fn = new_fn.replace('_', '')

    ## add ext back
    if ext:
        new_fn = new_fn + ext

    return new_fn


#______________________________________________________________________________
def rename(fn, new_fn):
    print '  Renaming %s' % fn
    print '        to %s' % new_fn
    os.rename(fn, new_fn)


#______________________________________________________________________________
def fatal(message=''):
    sys.exit("Fatal error in %s: %s" % (__file__, message))


#______________________________________________________________________________
def tprint(s, log=None):
    line = '[%s] %s' % (time.strftime('%Y-%m-%d:%H:%M:%S'), s)
    print line
    if log:
        log.write(line + '\n')
        log.flush()


#------------------------------------------------------------------------------
if __name__ == '__main__': main()

# EOF
