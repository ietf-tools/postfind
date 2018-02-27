#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright The IETF Trust 2018, All Rights Reserved

"""
NAME
  postfind - Follow a message (by Message-ID) in postfix logs

...

DESCRIPTION
  Given a Message-ID and one or more postfix log files as arguments, try to
  identify and follow the message's movement through the postfix pipeline.

OPTIONS
...

AUTHOR
  Written by Henrik Levkowetz, <henrik@levkowetz.com>

COPYRIGHT
  Copyright (c) 2018, The IETF Trust.  All rights reserved.

  Licenced under the 3-clause BSD license; see the file LICENSE
  for details.
"""

from __future__ import print_function, unicode_literals, division

import argparse
import debug
import os
import sys
import postfind

from postfind.finder import find
from pathlib2 import Path

_prolog, _middle, _epilog = __doc__.split('...')


class Options(object):
    def __init__(self, **kwargs):
        for (k, v) in kwargs.items():
            if not k.startswith('__'):
                setattr(self, k, v)
    pass


# ----------------------------------------------------------------------
#
# This is the entrypoint which is invoked from command-line scripts:

def run():

    global _prolog, _middle, _epilog

    program = os.path.basename(sys.argv[0])
    #progdir = os.path.dirname(sys.argv[0])

    # ----------------------------------------------------------------------
    # Parse config file
    # default values
    conf = {
    }
    for p in ['.', os.environ.get('HOME', '.'), '/etc/', ]:
        rcpath = Path(p)
        if rcpath.exists():
            rcfn = rcpath / ('.%src'%(program,))
            if rcfn.exists():
                execfile(str(rcfn), conf)
                break
    options = Options(**conf)
    options.program = program

    # ----------------------------------------------------------------------
    def say(s):
        msg = "%s\n" % (s)
        sys.stderr.write(msg)

    # ----------------------------------------------------------------------
    def note(s):
        msg = "%s\n" % (s)
        if not options.quiet:
            sys.stderr.write(msg)

    # ----------------------------------------------------------------------
    def die(s, error=1):
        msg = "\n%s: error:  %s\n\n" % (program, s)
        sys.stderr.write(msg)
        sys.exit(error)

    # ----------------------------------------------------------------------
    # Parse options

    default_tout = 60

    def commalist(value):
        return [ s.strip() for s in value.split(',') ]

    class HelpFormatter(argparse.RawDescriptionHelpFormatter):
        def _format_usage(self, usage, actions, groups, prefix):
            global _prolog
            if prefix is None or prefix == 'usage: ':
                prefix = 'SYNOPSIS\n  '
            return _prolog+super(HelpFormatter, self)._format_usage(usage, actions, groups, prefix)

    parser = argparse.ArgumentParser(description=_middle, epilog=_epilog,
                                     formatter_class=HelpFormatter, add_help=False)

    group = parser.add_argument_group(argparse.SUPPRESS)

    group.add_argument('ID',                                            help="The email Message-ID to look for")
    group.add_argument('LOGFILE', nargs='+',                            help="postfix logfile to scan")
    group.add_argument('-d', '--debug', action='store_true',            help="turn on debugging")
    group.add_argument('-f', '--follow', action='store_true',           help="follow file from just before end of file")
    group.add_argument('-h', '--help', action='help',                   help="show this help message and exit")
    group.add_argument('-q', '--quiet', action='store_true',            help="be more quiet")
    group.add_argument('-V', '--version', action='version', version='%s %s'%(program, postfind.__version__),
                                                                        help="output version information, then exit")
    group.add_argument('-v', '--verbose', action='store_true',          help="be (slightly) more verbose")
    group.add_argument('-t', '--timeout', type=int, default=default_tout,
                                            help="with --follow: how long to follow (default %ds)"%(default_tout,))

    options = parser.parse_args(namespace=options)

    if options.debug:
        note('options: %s' % options.__dict__)

    if hasattr(globals(), 'debug'):
        debug.debug = options.debug

    id =    options.ID
    files = options.LOGFILE

    if options.follow and len(files) > 1:
        die("Cannot follow more than one file")
    if options.follow and files[0].endswith('.gz'):
        die("Cannot follow a .gz file")

    try:
        note("Looking for Message-ID: %s\n" % id)
        lines = find(id, files, options)
        for l in lines:
            print(l.rstrip())
    except KeyboardInterrupt as e:
        say("\nKeyboardInterrupt")
    except OSError as e:
        if "Timeout" in str(e):
            say("Timeout when looking for Message-ID: %s while following %s" % (id, files[0]))
        else:
            say("OS Error when looking for Message-ID: %s " % (id, ))
    except Exception as e:
        raise
        die(e)


if __name__ == '__main__':
    run()
    
