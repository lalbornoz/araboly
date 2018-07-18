#!/usr/bin/env python3
#
# Araboly 2000 Advanced Server SP4 -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucio Andrés Illanes Albornoz <lucio@lucioillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from ArabolyGenerals import ArabolyGenerals
from ArabolyMonad import ArabolyDecorator
from ArabolyState import ArabolyGameState, ArabolyOutputLevel
from ArabolyTypeClass import ArabolyTypeClass

@ArabolyDecorator(context={"state":ArabolyGameState.SETUP})
class ArabolySetupMode(ArabolyTypeClass):
    """XXX"""

    # {{{ dispatch_status(args, channel, context, output, status): XXX
    @staticmethod
    def dispatch_status(args, channel, context, output, status):
        if len(args):
            status = False
        else:
            output = ArabolyGenerals._push_output(channel, context, output, "Current Araboly status:", outputLevel=ArabolyOutputLevel.LEVEL_NODELAY)
            output = ArabolyGenerals._push_output(channel, context, output, "Max. players: {}".format(len(context.players["numMap"])), outputLevel=ArabolyOutputLevel.LEVEL_NODELAY)
            output = ArabolyGenerals._push_output(channel, context, output, "Players.....: {}".format(", ".join(context.players["byName"].keys())), outputLevel=ArabolyOutputLevel.LEVEL_NODELAY)
        return args, channel, context, output, status
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=0
