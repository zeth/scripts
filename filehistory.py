#!/usr/bin/env python
"""Recursively order a directory of files by last modified date."""

import os
import datetime

class ModifyHist(dict):
    """A sorted dictionary-like object of modifications."""

    def __init__(self, path = None, quiet = None):
        """Initialises the file history. 
        If no path is specfied then start from current working directory."""
        dict.__init__(self)
        if path:
            self.path = path
        else:
            self.path = os.getcwd()

        lstfiles = os.walk(self.path)
        for i in lstfiles:
            directory = i[0]
            for j in i[2]:
                filename = os.path.join(directory, j)
                try:
                    raw_mtime = os.stat(filename).st_mtime
                except OSError:
                    # File Errors
                    if not os.access(filename, os.R_OK):
                        # If we don't have permission to read the file.
                        
                        # Make a fake time.
                        # 1 am on the first of January, 1970.
                        # The start of the 32bit epoch.
                        # I won't be born until over a decade later,
                        # So I won't have files that old.
                        raw_mtime = 0000000000.0
                        if not quiet:
                            print "We do not have permission to read", filename
                        
                    elif os.path.islink(filename):
                        # If the file is a broken symlink.
                        raw_mtime = os.lstat(filename).st_mtime
                        if not quiet:
                            print "Warning the following symlink", filename, \
                            "appears to be broken."
                    else:
                        # Some other problem, lets just give up.
                        raise
                
                mtime = datetime.datetime.fromtimestamp(raw_mtime)
                self[mtime] = filename

    def keys(self):
        """"D.keys() -> list of D's mtimes."""
        keys = dict.keys(self)
        keys.sort(reverse=True)
        return keys

def main():
    """Print out modified files within the directory."""
    from optparse import OptionParser
    usage = "usage: %prog [options] [directory path]"
    parser = OptionParser(usage = usage)
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose",
                      default=False,
                      help="output timestamps as well as filenames")
    parser.add_option("-q", "--quiet",
                      action="store_true", dest="quiet",
                      default=False,
                      help="supress error messages")
    parser.add_option("-n", "--lines",
                      action="store", type="int", dest="lines",
                      default=False,
                      help="output the last N lines")
    (options, args) = parser.parse_args()

    if args:
        path = args[0]
    else:
        path = os.getcwd()
    myhist = ModifyHist(path, options.quiet)

    if options.lines:
        for i in myhist.keys()[:options.lines]:
            if options.verbose:
                print myhist[i], i
            else:
                print myhist[i]

    else:
        for i in myhist.keys():
            if options.verbose:
                print myhist[i], i
            else:
                print myhist[i]

# start the ball rolling
if __name__ == "__main__": 
    main()

