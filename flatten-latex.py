#!/usr/bin/env python
import sys
import os
import re

inputPattern = re.compile('\\input{(.*)}')

def flattenLatex( rootFilename ):
    dirpath, filename = os.path.split(rootFilename)
    with open(rootFilename,'r') as fh:
        for line in fh:
            match = inputPattern.search( line )
            if match:
                newFile = match.group(1)
                if not newFile.endswith('tex'):
                    newFile += '.tex'
                flattenLatex( os.path.join(dirpath,newFile) )
            else:
                sys.stdout.write(line)

if __name__ == "__main__":
    flattenLatex( sys.argv[1] )
