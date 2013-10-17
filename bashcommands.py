#!/usr/bin/python
# print bash commands

print "find . -type f -print0 | xargs -0 sed -i -c 's/\-lt/\-ne/g'"
print "sh -x 2013-05-28T*/*.check 2013-05-28T*/*.log"
print "tar --extract --file=file.tar.gz filename"
print "for i in *.end; do echo ${i%\.*}; done"
print "--- number of lines in a directory ---"
print "ls -1 targetdir | wc -l"
