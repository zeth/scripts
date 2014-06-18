#!/usr/bin/env python
"""Parse feed and create static include for webpage.
I run this as a cron job."""
import feedparser

URL = 'http://zeth.net/rss.html'
FILENAME = 'output.html'

def parsefeed(url):
    """Parse the feed and return the items as an HTML list."""
    feed = feedparser.parse(url)
    output = ""
    for i in feed.entries:
        try:
            print i.title, i.link
            output += '<li><a href="' + i.link + '">' +  i.title + '</a></li>\n'
        except UnicodeEncodeError:
            print "/nRejecting an item for misformed Unicode./nContinuing./n/n"
    return output

def main():
    """Save the list as an HTML file, ready to be included in a webpage."""
    output = parsefeed(URL)
    htmlinclude = open (FILENAME, 'w')
    htmlinclude.write(output)
    htmlinclude.close()

# start the ball rolling
if __name__ == "__main__":
    main()
