#!/usr/bin/env python
"""Really lazy webpage - list of files in a directory."""

#####################################################################
# Configuration variables
#
# Path to where files are stored. 
FILEPATH = './'
#
# Path to where files are publically available.
URLHIERARCHY = './'
#
# Page Title
TITLE = 'Conference Papers: By Author'
#
# Path to Optional Template files.
# If used they will replace the below template.
# Don't forget to add quote marks. 
#
HEADER = None
FOOTER = None
#
#
# Default Webpage template
#
WEBPAGE = """Content-Type: text/html\n
 <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
         "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
 <html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
 <head>
 <meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
 <title>%(title)s</title>
 </head>
 <body>
 <h1>%(title)s</h1>
   <ul>%(content)s</ul>
 </body>
 </html>"""
#
#####################################################################

def createlinks(fpath, upath):
    """Make a hyperlink for every file in the directory"""
    import os
    files = os.listdir(fpath)
    links = []
    for i in files:
        links.append( '<li><a href="' + \
        upath + i + '">' + i.split('.')[0].replace('_', ' ') + '</a></li>')
    stringy = "\n".join(links)  
    return stringy

def loadtemplates():
    """Loads templates and constructs an HTML page."""
    try:
        fhead = file(HEADER)
        ffoot = file(FOOTER)
        webpag = """Content-Type: text/html\n
        """
        webpag += fhead.read()
        webpag += '<h1>%(title)s</h1>'
        webpag += '<ul>%(content)s</ul>'
        webpag += ffoot.read()
        fhead.close()
        ffoot.close()
        return webpag
    except IOError:
        return None

def main():
    """This runs when the file is called directly or via cgi."""
    webpage = WEBPAGE
    if HEADER and FOOTER:
        template = loadtemplates()
        if template:
            webpage = template
    
    print webpage % \
          {'title':TITLE, 'content': createlinks(FILEPATH, URLHIERARCHY)}

# start the ball rolling
if __name__ == "__main__":
    main()
