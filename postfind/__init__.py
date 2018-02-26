# Copyright 2018 the IETF Trust, All Rights Reserved
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division

__version__ = '0.1.1'

__date__    = "$Date:$"

__rev__     = "$Rev:$"

__id__      = "$Id:$"


# ----------------------------------------------------------------------

import collections
import os
import re
import tailer
import time


def inspect(seen, qnums, id, line):
    found = set()
    qnum = None
    qnum_line = re.search(r'postfix/[a-z]+\[[0-9]+\]: ([0-9A-F]{11}): ', line)
    if qnum_line != None:
        qnum = qnum_line.group(1)
        seen.append((qnum, line))
    id_line = re.search(r' message-id=<%s>'%re.escape(id), line)
    if id_line and qnum:
        # postfix log line
        qnums.add(qnum)
        for (q, l) in seen:
            if q == qnum:
                found.add(l)
    if qnum in qnums:
        found.add(line)
    if qnum and re.search(r'postfix/[a-z]+\[[0-9]+\]: %s: removed'%(qnum,), line):
        if qnum in qnums:
            qnums.remove(qnum)
    return found

def find(id, files, options):
    seen = collections.deque([], 100)
    qnums = set()
    found = set()
    stop_time = time.time() + options.timeout

    for filename in files:
        try:
            if filename.endswith('.gz'):
                import gzip
                file = gzip.open(filename)
            else:
                file = open(filename)
            if options.follow:
                ffile = tailer.follow(file)
                # position to approx. 1000 lines before end
                file.seek(-100000, os.SEEK_END)
                file.readline()
            for line in file:
                lines = inspect(seen, qnums, id, line.rstrip())
                found |= lines
                if found and not qnums:
                    break
            if options.follow:
                for line in ffile:
                    lines = inspect(seen, qnums, id, line.rstrip())
                    if lines:
                        found |= lines
                        stop_time = time.time() + options.timeout                        
                    if found and not qnums:
                        break
                    if time.time() > stop_time:
                        raise OSError("Timeout")
            file.close()
        except OSError:
            file.close()
            raise
        if found and not qnums:
            break

    found = list(found)
    found.sort()
    return found
