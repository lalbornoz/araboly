#!/usr/bin/env python3
#
# Araboly NT 3.1 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from ArabolyTypeClass import ArabolyTypeClass
from random import random

class ArabolyDaʕat(ArabolyTypeClass):
    """رب صدفة خير من ألف ميعاد"""

    # {{{ dispatch_dice(self, **params): XXX
    def dispatch_dice(self, **params):
        return {"dice":[int((random() * (6 - 1)) + 1), int((random() * (6 - 1)) + 1)], **params}
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120
