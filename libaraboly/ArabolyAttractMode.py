#!/usr/bin/env python3
#
# Araboly 2000 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucio Andrés Illanes Albornoz <lucio@lucioillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from ArabolyFree import ArabolyFree
from ArabolyMonad import ArabolyDecorator
from ArabolyRtl import ArabolyRandom
from ArabolyState import ArabolyGameState, ArabolyOutputLevel
from ArabolyTypeClass import ArabolyTypeClass
import time

@ArabolyDecorator(context={"state":ArabolyGameState.ATTRACT})
class ArabolyAttractMode(ArabolyTypeClass):
    """XXX"""

    # {{{ dispatch_start(args, channel, context, output, src, status): XXX
    @staticmethod
    def dispatch_start(args, channel, context, output, src, status):
        if len(args) != 1 or not args[0].isdigit()  \
        or int(args[0]) < 2 or int(args[0]) > 6:
            status = False
        else:
            players = int(args[0])
            context.players["byName"] = {src:{"field":0, "name":src, "num":0, "properties":[], "wallet":1500}}
            context.players["curNum"] = 0
            context.players["numMap"] = [None] * players
            context.players["numMap"][0] = src
            context.state = ArabolyGameState.SETUP
            output = ArabolyFree._push_output(channel, context, output, "Starting Araboly game with {players} players!".format(**locals()))
            output = ArabolyFree._push_output(channel, context, output, "Player {src} joins Araboly game!".format(**locals()))
        return args, channel, context, output, src, status
    # }}}
    # {{{ dispatch_status(args, channel, context, output, src, status): XXX
    @staticmethod
    def dispatch_status(args, channel, context, output, src, status):
        if len(args) != 0:
            status = False
        else:
            output = ArabolyFree._push_output(channel, context, output, "{src}: no game is in progress or has been started!".format(**locals()))
        return args, channel, context, output, src, status
    # }}}
    # {{{ dispatchTimer(channel, context, nextExpire, output, subtype): XXX
    @staticmethod
    def dispatchTimer(channel, context, nextExpire, output, subtype):
        if subtype == "attract":
            for attractLine in context.graphics["attract"][ArabolyRandom(limit=len(context.graphics["attract"]))]:
                output = ArabolyFree._push_output(channel, context, output, attractLine.rstrip("\n"), outputLevel=ArabolyOutputLevel.LEVEL_GRAPHICS)
            output += [{"eventType":"timer", "channel":channel, "expire":nextExpire, "nextExpire":nextExpire, "subtype":"attract"}]
        return channel, context, nextExpire, output, subtype
    # }}}

    # {{{ _enter(channel, context, output): XXX
    @staticmethod
    def _enter(channel, context, output):
        for logoLine in context.graphics["logo"]:
            output += [{"eventType":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, logoLine.rstrip("\n")]}]
        output += [{"eventType":"timer", "channel":channel, "expire":900, "nextExpire":900, "subtype":"attract"}]
        context.state = ArabolyGameState.ATTRACT
        return output
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=0
