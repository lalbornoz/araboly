#!/usr/bin/env python3
#
# Araboly 2000 Advanced Server SP4 -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from ArabolyGenerals import ArabolyGenerals
from ArabolyMonad import ArabolyDecorator
from ArabolyState import ArabolyGameState, ArabolyOutputLevel
from ArabolyTypeClass import ArabolyTypeClass

@ArabolyDecorator(context={"state":ArabolyGameState.SETUP})
class ArabolySetupMode(ArabolyTypeClass):
    """XXX"""

    # {{{ dispatch_start(args, channel, context, output, src, status): XXX
    @staticmethod
    def dispatch_start(args, channel, context, output, src, status):
        if not src == context.players["numMap"][0]  \
        or len(args):
            status = False
        else:
            playerList = [n for n in context.players["numMap"] if n != None]
            if len(playerList) <= 1:
                status = False
            else:
                output = ArabolyGenerals._push_output(channel, context, output, "Araboly game with {} players has started!".format(len(playerList)))
                output = ArabolyGenerals._push_output(channel, context, output, "Difficulty: {}".format(context.players["difficulty"]))
                output = ArabolyGenerals._push_output(channel, context, output, "Maximum player limit: {}".format(len(context.players["numMap"])))
                output = ArabolyGenerals._push_output(channel, context, output, "{numMap[0]}: roll the dice!".format(**context.players))
                context.players["curNum"] = 0
                context.state = ArabolyGameState.GAME
        return args, channel, context, output, src, status
    # }}}
    # {{{ dispatch_status(args, channel, context, output, status): XXX
    @staticmethod
    def dispatch_status(args, channel, context, output, status):
        if len(args):
            status = False
        else:
            output = ArabolyGenerals._push_output(channel, context, output, "Current Araboly status:", outputLevel=ArabolyOutputLevel.LEVEL_NODELAY)
            output = ArabolyGenerals._push_output(channel, context, output, "Difficulty..: {}".format(context.players["difficulty"]), outputLevel=ArabolyOutputLevel.LEVEL_NODELAY)
            output = ArabolyGenerals._push_output(channel, context, output, "Max. players: {}".format(len(context.players["numMap"])), outputLevel=ArabolyOutputLevel.LEVEL_NODELAY)
            output = ArabolyGenerals._push_output(channel, context, output, "Players.....: {}".format(", ".join(context.players["byName"].keys())), outputLevel=ArabolyOutputLevel.LEVEL_NODELAY)
        return args, channel, context, output, status
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=0
