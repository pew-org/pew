#!/usr/bin/env python

import sys, os

args = sys.argv[1:]
print('Running test template with args %s' % args)
project = args[0]
filename = os.path.join(args[1], 'TEST_FILE')
print('Writing to %s' % os.path.abspath(filename))
with open(filename, 'w') as output:
    output.write('\n'.join(args))
