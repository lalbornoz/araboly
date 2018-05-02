#!/usr/bin/env python3
#
# Araboly NT 4.0 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from ArabolyGame import ArabolyGameState
from ArabolyRtl import ArabolyRandom
from ArabolyTypeClass import ArabolyTypeClass

class ArabolyDaʕat(ArabolyTypeClass):
    """رب صدفة خير من ألف ميعاد"""

    # {{{ dispatch_dice(self, **params): XXX
    def dispatch_dice(self, **params):
        return {"dice":[ArabolyRandom(max=6, min=1), ArabolyRandom(max=6, min=1)], **params}
    # }}}
    # {{{ dispatchTimer(self, context, output, subtype, **params): XXX
    def dispatchTimer(self, context, output, subtype, **params):
        if subtype == "attract":
            channel = params["channel"]; nextExpire = params["nextExpire"];
            if context.state == ArabolyGameState.ATTRACT:
                for attractLine in context.attractLinesList[ArabolyRandom(limit=len(context.attractLinesList))]:
                    output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, attractLine.rstrip("\n")]}]
            output += [{"type":"timer", "channel":channel, "expire":nextExpire, "nextExpire":nextExpire, "subtype":"attract"}]
        return {"context":context, "output":output, "subtype":subtype, **params}
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120
