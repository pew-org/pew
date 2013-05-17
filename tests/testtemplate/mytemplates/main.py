#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2010 Doug Hellmann.  All rights reserved.
#
"""virtualenvwrapper.project plugin for tests
"""

import logging
import os

log = logging.getLogger(__name__)

def template(args):
    """Creates a test file containing the args passed to us
    """
    log.info('Running test template with args %r', args)
    project = args[0]
    filename = 'TEST_FILE'
    log.info('Writing to %s', filename)
    output = open(filename, 'w')
    try:
        output.write('\n'.join(args))
    finally:
        output.close()
    return
