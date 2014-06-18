#!/usr/bin/env python
"""Batch administration of moinmoin users. Make backups first.
Not tested outside of my install, use at your own risk.
Run from inside the user directory (inside data)."""

import os

def parse_moin_file(user_file_directory = './',
                    ignore_files = ('.trail', '.py', '.pyc',
                                    '.txt', '~', '#', 'README' )):
    """Parses user files into dictionary of names and filenames."""
    moinusers = {}
    for moinfile in os.listdir(user_file_directory):
        if not [moinfile for i in ignore_files if moinfile.endswith(i)]:
            try:
                username = open(moinfile).readlines()[15].rstrip()[5:]
                moinusers[username] = moinfile
            except IndexError:
                print "Rejecting: ", moinfile
    return moinusers


def dirty_admin(userdict):
    """Basic and simple interactive session.
    Could be replaced by something posher
    such as a web frontend."""
    newknownusers = []
    newdeletedusers = []
    print "Type y for users you want to delete."
    print "Type n for users you wish to keep."
    print "To quit, type Ctrl+C."
    print "\n\n"
    for i in userdict:
        print i
        answerd = raw_input()
        if answerd == 'y':
            newdeletedusers.append(i)
        elif answerd == 'n':
            newknownusers.append(i)
        else:
            print "I only understand y or n. ", i, " kept."
            newknownusers.append(i)
    print "End of Users."
    print "We are going to keep and write to known users:"
    for i in newknownusers:
        print i,
    print "\nWe are going to delete:"
    for i in newdeletedusers:
        print i,
    print "\nDo you want to continue?"
    lastchance = raw_input()
    if lastchance != 'y':
        print "Operation Aborted"
        import sys
        sys.exit()
    return newknownusers, newdeletedusers

def parse_known_user_file(filename = './KnownUsers.txt'):
    """Load the known users."""
    try:
        knownusers = [i.rstrip() for i in open(filename).readlines()]
    except IOError:
        knownusers = []
    return knownusers

def append_known_users(newusers, filename = './KnownUsers.txt'):
    """Add users to the known users list."""
    knownuserfile = open(filename, 'a')
    for i in newusers:
        knownuserfile.write(i + '\n')
    knownuserfile.close()

def delete_unwanted_users(users_to_be_killed, userdictionary,
                          user_file_directory = './'):
    """Remove unwanted users from the user directory."""
    for i in users_to_be_killed:
        victim = userdictionary[i]
        os.remove(victim)
        os.remove(user_file_directory + victim + '.trail')

def main():
    """Start the Interactive session when called directly."""
    ourusers = parse_moin_file()
    knownusers = parse_known_user_file()
    skippedusers = [ourusers.pop(i, 'None') for i in knownusers]
    newknown, newdeleted = dirty_admin(ourusers)
    savedusers = [ourusers.pop(i, 'None') for i in newknown]
    append_known_users(newknown)
    delete_unwanted_users(newdeleted, ourusers)
    

if __name__ == "__main__":
    main()
        
