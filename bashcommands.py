#!/usr/bin/python
# print bash commands

print "find . -type f -print0 | xargs -0 sed -i -c 's/\-lt/\-ne/g'"
