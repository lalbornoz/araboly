#!/usr/bin/env python3
#
# Araboly NT 4.0 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucio Andrés Illanes Albornoz <lucio@lucioillanes.de>
# This project is licensed under the terms of the MIT licence.
#

import os, sys

# {{{ ArabolyAlignedReplace(old, patterns, new): XXX
def ArabolyAlignedReplace(old, patterns, new):
    patIdx = 0; patternLen = len(patterns[0]);
    newLen = min(len(new), patternLen * len(patterns))
    for idx in range(0, newLen, patternLen):
        if (idx + patternLen) > newLen:
            replace  = (" " * int((patternLen - len(new[idx:])) / 2)) + new[idx:]
            replace += (" " * int((patternLen - len(replace))))
        else:
            replace = new[idx:idx+patternLen]
        old = old.replace(patterns[patIdx], replace); patIdx += 1;
    if patIdx < len(patterns):
        for pattern in patterns[patIdx:]:
            old = old.replace(pattern, " " * len(pattern))
    return old
# }}}
# {{{ ArabolyRandom(limit=None, max=None, min=0): XXX
def ArabolyRandom(limit=None, max=None, min=0):
    randomInt = int.from_bytes(os.urandom(1), byteorder=sys.byteorder)
    if max != None:
        limit = max + 1
    elif limit != None:
        limit = limit
    else:
        raise ValueError
    return (randomInt % (limit - min)) + min
# }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120
