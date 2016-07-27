#!/usr/bin/env python
"""
NAME
    pdf_librarian.py - short description

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
    Copyright 2016 Ryan Reece
    License: GPL <http://www.gnu.org/licenses/gpl.html>

SEE ALSO
    ROOT <http://root.cern.ch>

TO DO
    - One.
    - Two.

2016-03-15
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
from PyPDF2 import PdfFileReader

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
    parser.add_argument('infiles', nargs='*', default=None,
            help='Input files.')
    parser.add_argument('-a', '--always',  default=False,  action='store_true',
            help="Always check Google Scholar to update file names.")
    return parser.parse_args()


#------------------------------------------------------------------------------
# main
#------------------------------------------------------------------------------
def main():
    ops = options()

    input_files = get_input_files()

    print '|'

    rex_good_filename = r'\d\d\d\d?(BCE)?\.[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+\.pdf'
    rex_near_filename = r'\d\d\d\d?(BCE)?\.[^.]+\.[^.]+\.(pdf|PDF)'

    new_filenames = []
    good_filenames = []

    for fn in input_files:

        ## skip files that are not pdfs
        if not re.match(r'.+\.(pdf|PDF)', fn):
            print '| Skipping file (not a pdf): %s' % fn
            continue

        ## check if filename is "good"
        if re.match(rex_good_filename, fn):
            print '| Good filename: %s' % fn
            good_filenames.append(fn)

            fn_parts = fn.split('.')
            year, author, title, pdf = fn_parts
            year = int(year)
            title = title.replace('-', ' ')

#            if ops.always:
#
#            else:
#                ## ask if the default name is ok
#                print '| The corrected file name defaults to: %s' % new_fn
#                uin = raw_input('| Would you like to rename the file to this? [y/n]: ').strip()
#
#                if uin == 'y' or uin == 'Y':
#                    rename(fn, new_fn)
#

            cmd_template = r'scholar.py --no-patents --title-only --author "%s" --after %i --before %i --phrase "%s" --citation=bt'
            bibtex = subprocess.check_output(cmd_template % (author, year, year, title), stderr=subprocess.STDOUT, shell=True)

            if not bibtex:
                title = title.replace('QFT', 'Quantum Field Theory')
                print cmd_template % (author, year-1, year+1, title)
                bibtex = subprocess.check_output(cmd_template % (author, year-1, year+1, title), stderr=subprocess.STDOUT, shell=True)

                if not bibtex:
                    print '| Nothing found!'

            print bibtex.split('@')


        ## automatically fix files that are nearly good
        elif re.match(rex_near_filename, fn):
            print '| Fixing file: %s' % fn
            new_fn = fix_filename(fn)
            rename(fn, new_fn)
            new_filenames.append(new_fn)
            good_filenames.append(new_fn)

        ## ask the user for help
        else:
            print '|'
            print '| File: %s' % fn
            print '|   is not close to having a good name.' 

            ## try to use the metadata first
            meta = get_pdf_metadata(fn)
            if meta:
                print '| The pdf metadata: %s' % meta
                new_fn = make_default_filename(fn, meta)
                new_fn = fix_filename(new_fn)

            ## ask if the default name is ok
            print '| The corrected file name defaults to: %s' % new_fn
            uin = raw_input('| Would you like to rename the file to this? [y/n]: ').strip()

            if uin == 'y' or uin == 'Y':
                rename(fn, new_fn)
                new_filenames.append(new_fn)
                good_filenames.append(new_fn)
            
            else:
                ## ask if the user would like to enter a better name
                uin = raw_input('| Would you like to enter a better one? [y/n]: ').strip()
                if uin == 'y' or uin == 'Y':
                    p = subprocess.Popen('open %s' % fn.replace(' ', r'\ '), shell=True)
                    uin = raw_input('| New file name (empty => skip): ').strip()
                    p.terminate()  # Seems to do nothing. Apple Preview stays open.

                    if uin:
                        print '| You suggest: %s' % uin
                        new_fn = fix_filename(uin)
                        rename(fn, new_fn)
                        new_filenames.append(new_fn)
                        good_filenames.append(new_fn)

                    else:
                        print '| Skipping file.'
            
                else:
                    print '| Skipping file.'


    print '|'
    print '| %i files renamed:' % len(new_filenames)
    print '|'
    for fn in new_filenames:
        print '| %s' % fn
    print '|'

    write_index_md(good_filenames)
    print '|'




#------------------------------------------------------------------------------
# free functions
#------------------------------------------------------------------------------

#______________________________________________________________________________
def get_input_files():
    ops = options()

    input_files = list()

    if ops.infiles:
        input_files = list(ops.infiles)
    else:
        print '| You can give some input pdf files as arguments. Assuming *.pdf'
        input_files = glob.glob('*.pdf')
        input_files.extend(glob.glob('*.PDF'))

    if len(input_files) == 0:
        fatal('| You should give some input pdf files as arguments.')

    return input_files

#______________________________________________________________________________
def clean_filename(fn):
    new_fn = str(fn)

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
    new_fn = new_fn.replace('.-', '.')
    new_fn = new_fn.replace('-.', '.')

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

    return new_fn


#______________________________________________________________________________
def fix_filename(fn):
    new_fn = str(fn)

    new_fn = clean_filename(fn)

    ## fix suffix
    if not new_fn.endswith('.pdf'):
        if new_fn.endswith('.PDF'): ## remove capitalization
            new_fn = '%s.pdf' % os.path.splitext(new_fn)

    ## e.g. 1969.Quine.Natural-Kinds.pdf
    assert new_fn.count('.') == 3, new_fn
    s_date, s_authors, s_title, pdf = new_fn.split('.')

    ## capitalize authors
    authors = s_authors.split('-')
    c_authors = list()
    for author in authors:
        if not (author.istitle() or author.isupper()):
            author = author.capitalize()
        c_authors.append(author)
    s_authors = '-'.join(c_authors)

    ## capitalize the first word of the title. others comes as they are.
    title_words = s_title.split('-')
    title_word0 = title_words[0]
    if not (title_word0.istitle() or title_word0.isupper()):
        title_words[0] = title_words[0].capitalize()
    s_title = '-'.join(title_words)

    new_fn_parts = [s_date, s_authors, s_title, pdf]
    new_fn = '.'.join(new_fn_parts)

    return new_fn


#______________________________________________________________________________
def make_default_filename(fn, meta):
    new_fn = str(fn)

    new_fn = clean_filename(fn)
    root, ext = os.path.splitext(new_fn) # ext = '.pdf'
    root = root.replace('.', '-')

    if not meta.has_key('year'): # always not in pdf
#        meta['year'] = time.strftime('%Y') # use the current year as a placeholder
        meta['year'] = 1900 # use 1900 as the year placeholder
    
    if not (meta.has_key('author') and meta['author'] and meta['author'].lower() != 'none'):
        meta['author'] = 'Author'
    
    if not (meta.has_key('title') and meta['title'] and meta['title'].lower() != 'none'):
        meta['title'] = root

    new_fn = '%(year)s.%(author)s.%(title)s.pdf' % meta

    return new_fn


#______________________________________________________________________________
def get_pdf_metadata(fn):

    meta = dict()

    try:
        with open(os.path.abspath(fn), "rb") as pdf_file:
            pdf = PdfFileReader(pdf_file)
#            if pdf.isEncrypted:
#                pdf.decrypt('')
            meta['author']   = pdf.getDocumentInfo().author
            meta['creator']  = pdf.getDocumentInfo().creator
            meta['producer'] = pdf.getDocumentInfo().producer
            meta['subject']  = pdf.getDocumentInfo().subject
            meta['title']    = pdf.getDocumentInfo().title 

    except Exception as e:
        print e
        print 'file: %s' % fn

    return meta


#______________________________________________________________________________
def rename(fn, new_fn):
    print '| Renaming %s' % fn
    print '|       to %s' % new_fn
    os.rename(fn, new_fn)


#______________________________________________________________________________
def write_index_md(good_filenames):
    out = open('index.md', 'w')
    for fn in good_filenames:
        out.write('1.  %s\n' % (fn))
    out.close()
    print '| index.md written.'


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
