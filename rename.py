#!/usr/bin/env python
# coding: utf-8
"""
Author: Matt Weber
Date:   03/04/07

Renames files based on the input options.
Author: Petr Moses
Date:   08/06/15
Remove spaces and diacritics
"""

# from __future__ import unicode_literals
import glob, os
import sys
import re
import unicodedata
import six
import win_unicode_console
from optparse import OptionParser


def to_unicode_or_bust(obj, encoding='utf-8'):
    if six.PY2:
        if isinstance(obj, basestring):
            if not isinstance(obj, unicode):
                obj = unicode(obj, encoding)
    return obj


def renamefile(options, filepath):
    """
    Renames a file with the given options
    """
    # split the pathname and filename
    pathname = to_unicode_or_bust(os.path.dirname(filepath),  sys.getfilesystemencoding())
    filename = to_unicode_or_bust(os.path.basename(filepath), sys.getfilesystemencoding())

    # trim characters from the front
    if options.trimfront:
        filename = filename[options.trimfront:]

    # trim characters from the back
    if options.trimback:
        filename = filename[:len(filename) - options.trimback]

    # replace values if any
    if options.replace:
        for vals in options.replace:
            filename = filename.replace(vals[0], vals[1])

    # remove diacritics if flag set
    if options.diacritics:
        filename = ''.join((c for c in unicodedata.normalize('NFD', filename) if unicodedata.category(c) != 'Mn'))
        # filename = unicodedata.normalize('NFKD', filename)

    # remove spaces if flag set
    if options.spaces:
        filename = re.sub(u'[\s\-\_]+', '-', filename)
        filename = re.sub(u'[\-]+^', '', filename)
        filename = re.sub(u'[\-]+\.', '.', filename)

    # convert to lowercase if flag set
    if options.lowercase:
        filename = filename.lower()

    # create the new pathname and rename the file
    new_filepath = os.path.join(pathname, filename)
    try:
        # check for verbose output
        if options.verbose:
            # print(u"{0} -> {1}".format(filepath, new_filepath).encode(sys.stdout.encoding,'ignore'))
            print(u"{0} -> {1}".format(filepath, new_filepath))
            # print(u"{0}".format(new_filepath))

        if not options.test:
            os.rename(filepath, new_filepath)
    except OSError as ex:
        # print((u"Error renaming '{0}': {1}".format(filepath, ex.strerror).encode("utf-8")), file=sys.stderr)
        sys.stderr.buffer.write(
            "Error renaming '{0}': {1} /n".format(filepath, ex.strerror))


if __name__ == "__main__":
    win_unicode_console.enable()
    """
    Parses command line and renames the files passed in
    """

    # create the options we want to parse
    usage = "usage: %prog [options] file1 ... fileN"
    optParser = OptionParser(usage=usage)
    optParser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False,
                         help="Use verbose output")
    optParser.add_option("-l", "--lowercase", action="store_true", dest="lowercase", default=False,
                         help="Convert the filename to lowercase")
    optParser.add_option("-d", "--diacritics", action="store_true", dest="diacritics", default=False,
                         help="Remove diacritics from filename")
    optParser.add_option("-s", "--spaces", action="store_true", dest="spaces", default=False,
                         help="Remove spaces from filename")
    optParser.add_option("-f", "--trim-front", type="int", dest="trimfront", metavar="NUM",
                         help="Trims NUM of characters from the front of the filename")
    optParser.add_option("-b", "--trim-back", type="int", dest="trimback", metavar="NUM",
                         help="Trims NUM of characters from the back of the filename")
    optParser.add_option("-r", "--replace", action="append", type="string", nargs=2, dest="replace",
                         help="Replaces OLDVAL with NEWVAL in the filename", metavar="OLDVAL NEWVAL")
    optParser.add_option("-t", "--test", action="store_true", dest="test",
                         help="Only dry test, without renaming files", default=False)
    (options, args) = optParser.parse_args()

    # check that they passed in atleast one file to rename
    if len(args) < 1:
        optParser.error("Files to rename not specified")

    # loop though the files and rename them
    for filepattern in args:
        for filename in glob.glob(filepattern):
            renamefile(options, filename)

    # exit successful
    sys.exit(0)
