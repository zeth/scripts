#!/usr/bin/env python

# Twitnotify.py 0.1
# Copyright Zeth Green 2008
# See http://zeth.me.uk/python/

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Send Notifications about Twitter updates.
It assumes a GNOME based Linux/Unix system.

The first time it may seem a bit crazy if 
you have a lot of old Twitter updates. 

Four steps to install:

1. Install the three dependencies:

pynotify - available from your distribution.
e.g. sudo apt-get install python-notify
e.g. sudo emerge notify-python

simplejson - available from the cheeseshop.
e.g. sudo easy_install simplejson

python-twitter - available from the cheeseshop.
e.g. sudo easy_install python-twitter 

2. Get a Twitter account. Add some friends (e.g. zeth0).

3. Set up the USERNAME and PASSWORD below.

4. Run the script and (optionally) background it.

"""

import pygtk
pygtk.require('2.0')
import pynotify
import sys
#import gtk
import os
import twitter
import urllib
import pickle
import time

#####################################
# Change these to match your system

USERNAME = "zeth0"
PASSWORD = "lenna"

#####################################
# These should be fine for most users

STORAGE_DIRECTORY = "~/.twitter"
IMAGE_DIRECTORY = "~/.twitter/images"

#####################################


class TwitterStatus(object):
    """Manages your history of Twitter status updates."""

    def __init__(self):
        self.api = twitter.Api(username = USERNAME, password = PASSWORD)
        self.store = {}
        self.storage = os.path.expanduser(STORAGE_DIRECTORY)
        self.image_storage = os.path.expanduser(IMAGE_DIRECTORY)
        if not os.path.exists(self.image_storage):
            os.makedirs(self.image_storage)

    def save(self):
        """Save storage file to disk."""
        filename = open(self.storage + "/twitter.pkl", 'w')     
        pickle.dump(self.store, filename)
        filename.close()

    def load(self):
        """Load storage file from disk."""
        try:
            filename = open(self.storage + "/twitter.pkl", 'r')     
            self.store = pickle.load(filename)
            filename.close()
        except IOError:
            self.store = {}

    def check_status(self, status):
        """Check if a status update has already been stored.
        If not then store it and send a notification."""
        if status.id not in self.store.keys():
            # Deal with inconsistencies in the bindings
            try:
                username = status.user.name
            except AttributeError:
                username = status.sender_screen_name
            try:
                profile_image = status.user.profile_image_url
            except AttributeError:
                profile_image = self.api.GetUser(\
                                username).GetProfileImageUrl()

            # Find the image
            imagepath = self.cached_image(username)
            if not imagepath:
                imagepath = self.download_image(username, 
                            profile_image)

            # Markup Hyperlinks
            text = status.text
            if "http://" in text:
                for i in text.split():
                    if i.startswith("http://"):
                        text = text.replace(i, \
                               '<a href="' + i + '">' + i + '</a>')

            # Call notification
            send_note(username, text, imagepath )

            # Add to dict
            self.store[status.id] = status

    def download_image(self, username, image_url):
        """Download new profile image."""
        fileextension = image_url.rpartition('.')[-1]
        targetname = self.image_storage + "/" + username + "." + fileextension
        urllib.urlretrieve(image_url, targetname)
        return targetname

    def cached_image(self, username):
        """Check for already downloaded profile image."""
        for i in os.listdir(self.image_storage):
            if i.startswith(username + "."):
                return i
            else:
                return None

def send_note(user, message, imageurl):
    """Send the note to the desktop.""" 
    if not pynotify.init("Twitter Notify"):
        sys.exit(1)
    note = pynotify.Notification(user, message, imageurl)
    if not note.show():
        print "Failed to send notification"
        sys.exit(1)

def check_updates():
    """Check for Twitter Updates"""

    # Initiate 
    twit = TwitterStatus()

    # Load stored entries
    twit.load()    

    # Start with Friend Timeline
    for i in twit.api.GetFriendsTimeline():
        twit.check_status(i)

    # Next lets do Replies
    for i in twit.api.GetReplies():
        twit.check_status(i)

    # Personal Messages we have been sent
    for i in twit.api.GetDirectMessages():
        twit.check_status(i)

    # Save stored entries
    twit.save() 

def main():
    """When called directly, run and then repeat."""
    check_updates()
    print "Initial update completed."
    print "It will now repeat every 10 mins." 

    #Repeat every ten minutes
    while 1:
        try:
            time.sleep(600)
            check_updates()
        except KeyboardInterrupt:
            sys.exit(1)

if __name__ == '__main__':
    main()


