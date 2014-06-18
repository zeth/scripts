# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without any warranty.

"""Bazaar version script, use in a Python package that is version controlled
using Bazaar.

In the package's __init__.py put the following code or similar:

VERSION = "0.1"
def get_version(full = False):
    '''Return the version of the module'''
    from version import get_version_from_bazaar
    return get_version_from_bazaar(__path__, VERSION, full)

Then the user of a package can easily see an automatically generated
minor version number.

This can be helpful in providing support, i.e. ask the user to provide
the version number.

"""

__author__ = 'Zeth'
__author_email__ = 'theology@gmail.com'
__version__ = '1.0'
__copyright__ = 'Zeth'

def get_version_from_bazaar(version = __version__, full = False):
    """Returns the version number combined with the bzr revision number.
    Set `full` to True for revision id."""

    # If the user does not have bazaar, then return unknown
    try:
        from bzrlib.branch import Branch
        from bzrlib.errors import NotBranchError
    except ImportError:
        return version + "-unknown"

    import os
    # Save the old location
    start_dir = os.path.abspath(os.curdir)

    # Make sure we get the correct branch location.
    # Even with symlinks

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Try to use the branch.
    try:
        pixelise_branch = Branch.open_containing(os.path.abspath('.'))[0]
    except NotBranchError:
        # Oh well give up and go to the original directory.
        os.chdir(start_dir)
        return version + "-unknown"

    # Go to the original directory.
    os.chdir(start_dir)
    # Add the pixelise branch revison number to the version number.
    version_number = version + "-" + str(pixelise_branch.revno())
    if full:
        # If `full` is true then add the last revision too.
        version_number += "-" + pixelise_branch.last_revision()
    # Return the version number
    return version_number
