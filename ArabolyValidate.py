#!/usr/bin/env python3
#
# Araboly NT 3.1 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from ArabolyGame import ArabolyGameState
from ArabolyTypeClass import ArabolyTypeClass

class ArabolyValidate(ArabolyTypeClass):
    """XXX"""

    # {{{ dispatch_bid(self, args, context, status, **params): XXX
    def dispatch_bid(self, args, context, status, **params):
        if context.state != ArabolyGameState.AUCTION    \
        or len(args) != 1 or int(args[0]) <= 0:
            status = False
        else:
            params["price"] = int(args[0])
        return {"args":args, "context":context, "status":status, **params}
    # }}}
    # {{{ dispatch_board(self, args, context, status, **params): XXX
    def dispatch_board(self, args, context, status, **params):
        if  context.state != ArabolyGameState.GAME      \
        and context.state != ArabolyGameState.PROPERTY  \
        and context.state != ArabolyGameState.AUCTION:
            status = False
        elif len(args):
            status = False
        return {"args":args, "context":context, "status":status, **params}
    # }}}
    # {{{ dispatch_buy(self, args, context, src, status, **params): XXX
    def dispatch_buy(self, args, context, src, status, **params):
        if context.state != ArabolyGameState.PROPERTY   \
        or context.players[context.playerCur] != src \
        or len(args):
            status = False
        return {"args":args, "context":context, "src":src, "status":status, **params}
    # }}}
    # {{{ dispatch_cheat(self, args, context, status, **params): XXX
    def dispatch_cheat(self, args, context, status, **params):
        if  context.state != ArabolyGameState.GAME          \
        and context.state != ArabolyGameState.PROPERTY      \
        and context.state != ArabolyGameState.AUCTION:
            status = False
        elif context.players[context.playerCur] != player   \
        or   len(args):
            status = False
        return {"args":args, "context":context, "status":status, **params}
    # }}}
    # {{{ dispatch_develop(self, args, context, status, **params): XXX
    def dispatch_develop(self, args, context, status, **params):
        if  context.state != ArabolyGameState.GAME      \
        and context.state != ArabolyGameState.PROPERTY:
            status = False
        elif len(args) != 2:
            status = False
        else:
            params.update({"field":int(args[0]), "level":int(args[1])})
        return {"args":args, "context":context, "status":status, **params}
    # }}}
    # {{{ dispatch_dice(self, args, context, src, status, **params): XXX
    def dispatch_dice(self, args, context, src, status, **params):
        if context.state != ArabolyGameState.GAME       \
        or context.players[context.playerCur] != src    \
        or len(args):
            status = False
        return {"args":args, "context":context, "src":src, "status":status, **params}
    # }}}
    # {{{ dispatch_help(self, **params): XXX
    def dispatch_help(self, **params):
        return params
    # }}}
    # {{{ dispatch_join(self, args, context, src, status, **params): XXX
    def dispatch_join(self, args, context, src, status, **params):
        if context.state != ArabolyGameState.SETUP  \
        or src in context.players                   \
        or len(args):
            status = False
        return {"args":args, "context":context, "src":src, "status":status, **params}
    # }}}
    # {{{ dispatch_kick(self, args, context, src, status, **params): XXX
    def dispatch_kick(self, args, context, src, status, **params):
        if context.state == ArabolyGameState.DISABLED   \
        or len(args) != 1 or args[0] not in context.players:
            status = False
        elif src.lower() != "v!arab@127.0.0.1".lower():
            status = False
        else:
            params["otherPlayer"] = args[0]
        return {"args":args, "context":context, "src":src, "status":status, **params}
    # }}}
    # {{{ dispatch_part(self, args, context, src, status, **params): XXX
    def dispatch_part(self, args, context, src, status, **params):
        if  context.state != ArabolyGameState.SETUP     \
        and context.state != ArabolyGameState.GAME      \
        and context.state != ArabolyGameState.PROPERTY  \
        and context.state != ArabolyGameState.AUCTION:
            status = False
        elif src not in context.players                 \
        or   len(args):
            status = False
        return {"args":args, "context":context, "src":src, "status":status, **params}
    # }}}
    # {{{ dispatch_pass(self, args, context, src, status, **params): XXX
    def dispatch_pass(self, args, context, src, status, **params):
        if context.state == ArabolyGameState.PROPERTY:
            if context.players[context.playerCur] != src:
                status = False
        elif context.state != ArabolyGameState.AUCTION:
            status = False
        elif len(args):
            status = False
        return {"args":args, "context":context, "src":src, "status":status, **params}
    # }}}
    # {{{ dispatch_start(self, args, context, src, status, **params): XXX
    def dispatch_start(self, args, context, src, status, **params):
        if context.state != ArabolyGameState.ATTRACT    \
        or len(args) != 1:
            status = False
        else:
            params["players"] = int(args[0])
        return {"args":args, "context":context, "src":src, "status":status, **params}
    # }}}
    # {{{ dispatch_status(self, args, context, status, **params): XXX
    def dispatch_status(self, args, context, status, **params):
        if context.state == ArabolyGameState.DISABLED   \
        or len(args):
            status = False
        return {"args":args, "context":context, "status":status, **params}
    # }}}
    # {{{ dispatch_stop(self, args, context, src, status, **params): XXX
    def dispatch_stop(self, args, context, src, status, **params):
        if  context.state != ArabolyGameState.SETUP     \
        and context.state != ArabolyGameState.GAME      \
        and context.state != ArabolyGameState.PROPERTY  \
        and context.state != ArabolyGameState.AUCTION:
            status = False
        elif len(args):
            status = False
        elif src.lower() != "v!arab@127.0.0.1".lower():
            status = False
        return {"args":args, "context":context, "src":src, "status":status, **params}
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120
