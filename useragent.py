#!/usr/bin/env python
import os
print "Content-type: text/plain"
print
print "User-Agent:", os.environ.get("HTTP_USER_AGENT", "N/A")

