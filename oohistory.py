#!/usr/bin/env python
"""Print out all the available OpenOffice history."""

# Default path to History file
# ----------------------------
#
# I myself use a certain type of Linux. Change the PATH to match the 
# location of Common.xcu on your computer.
# Common.xcu will be in your home directory somewhere.

PATH = "~/.openoffice.org2/user/registry/data/org/openoffice/Office"

# Windows users may uncomment the lines below.
# Remember to replace zeth with your username.

#USERNAME = "zeth"

#PATH = "C:/Documents and Settings/" 
#PATH += USERNAME
#PATH += "/Application Data/OpenOffice.org"
#PATH += "/user/registry/data/org/openoffice/Office/Common.xcu"

import xml.etree.ElementTree

def get_history(filename):
    """Return the history as a list of URLs. """
    history = []
    tree = xml.etree.ElementTree.parse(filename)
    for toplevelnode in tree.getiterator('node'):
        if 'History' in toplevelnode.attrib.values():
            for secondlevelnode in toplevelnode:
                for attribname in secondlevelnode.attrib.values():
                    if attribname == 'List':
                        for node in secondlevelnode:
                            for prop in node:
                                if 'URL' in prop.attrib.values():
                                    history.append(prop[0].text)
    return history

def main():
    """Runs the main function if called directly."""
    from optparse import OptionParser
    usage = "usage: %prog [options] [history file]"
    parser = OptionParser(usage = usage)
    parser.add_option("-f", "--files",
                      action="store_false", dest="URLs",
                      default=True,
                      help="output local filenames rather than URLs")
    (options, args) = parser.parse_args()
    if args:
        filename = args[0]
    else:
        filename = PATH + "/Common.xcu"
        import os
        filename = os.path.expanduser(filename)

    if options.URLs:
        for i in get_history(filename):
            print i
    else:
        for i in get_history(filename):
            if i.startswith('file'):
                print i[7:]

# start the ball rolling
if __name__ == "__main__": 
    main()

