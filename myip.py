#!/usr/bin/env python
"""Show the IP Address of the browser. """

TEMPLATE = """Content-Type: text/html\n\n 
 <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
         "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
 <html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
 <head>
 <meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
 <title>IP Address</title>
 </head>
 <body>
   %s
 </body>
 </html>"""

import os

def main():
    """If called directly then show IP Address.
    It may well be a router rather than the local
    machine."""
    includes = os.environ['REMOTE_ADDR']
    print TEMPLATE % includes

# start the ball rolling
if __name__ == "__main__": 
    main()
    
