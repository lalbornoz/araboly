#!/usr/bin/env python3
#
# Araboly 2000 Advanced Server SP4 -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

import os, sys
sys.path.append(os.path.join(os.getcwd(), "libaraboly"))
sys.path.append(os.path.join(os.getcwd(), "libircbot"))
sys.path.append(os.path.join(os.getcwd(), "librtl"))

from ArabolyAttractMode import ArabolyAttractMode
from ArabolyAuctionMode import ArabolyAuctionMode
from ArabolyBankruptcyMode import ArabolyBankruptcyMode
from ArabolyEvents import ArabolyEvents
from ArabolyFree import ArabolyFree
from ArabolyGameMode import ArabolyGameMode
from ArabolyIrcClient import ArabolyIrcClient
from ArabolyIrcToCommandMap import ArabolyIrcToCommandMap
from ArabolyMonad import ArabolyMonad
from ArabolyPropertyMode import ArabolyPropertyMode
from ArabolySetupMode import ArabolySetupMode
from ArabolyState import ArabolyState
from ArabolyTrade import ArabolyTrade

class Araboly(object):
    """XXX"""
    optionsDefault = {}
    typeObjects = [ArabolyAttractMode, ArabolyAuctionMode, ArabolyBankruptcyMode, ArabolyGameMode, ArabolyFree, ArabolyIrcToCommandMap, ArabolyPropertyMode, ArabolySetupMode, ArabolyState, ArabolyTrade]

    # {{{ unit(self, event, **extra): XXX
    def unit(self, event, **extra):
        unit = ArabolyMonad(                                \
                context=self.typeObjects[ArabolyState],     \
                output=[], status=True, **event, **extra)
        unit = unit                                         \
                >> ArabolyIrcToCommandMap                   \
                >> ArabolyAttractMode                       \
                >> ArabolyAuctionMode                       \
                >> ArabolyBankruptcyMode                    \
                >> ArabolyGameMode                          \
                >> ArabolyPropertyMode                      \
                >> ArabolySetupMode                         \
                >> ArabolyTrade                             \
                >> ArabolyFree
        status = False if "exc_obj" in unit.params else True
        return status, unit.params["output"], unit.params.copy()
    # }}}
    # {{{ __init__(self, options): initialisation method
    def __init__(self, options):
        for optionName in [k for k in self.optionsDefault if k not in options]:
            options[optionName] = self.optionsDefault[optionName]
        self.options = options; typeObjects = {};
        for typeObject in self.typeObjects:
            if typeObject in [ArabolyEvents, ArabolyIrcClient, ArabolyState]:
                typeObjects[typeObject] = typeObject(**self.options)
            else:
                typeObjects[typeObject] = typeObject
        self.typeObjects = typeObjects
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=0
