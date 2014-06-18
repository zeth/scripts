#!/bin/sh
# pdfgrep
# Simple search command for PDF files.
# Requires that pdftotext is installed
# 
# I use it like this:
# pdfgrep -ic "text" *.pdf
#
# Only works for text-based PDFs of course.
# As PDFs only containing images have no text.
# For example, PDFs made by scanners.

case "$1" in -*) opts=$1; 
  shift ;; *) 
  opts="--" ;; 
esac
KEYWORDS="$1"
shift;
for PDF in "$@" ; do
printf "%s: " "$PDF"
pdftotext "$PDF" - | grep "$opts" "$KEYWORDS"
done

