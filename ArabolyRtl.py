#!/usr/bin/env python3
#
# Araboly NT 3.1 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

import os, sys

def ArabolyRandom(limit=None, max=None, min=0):
    randomInt = int.from_bytes(os.urandom(1), byteorder=sys.byteorder)
    if max != None:
        limit = max + 1
    elif limit != None:
        limit = limit
    else:
        raise ValueError
    return (randomInt % (limit - min)) + min

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120
