#!/usr/bin/env python3
#
# Araboly NT 3.1 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from ArabolyGame import ArabolyGameField, ArabolyGameState
from ArabolyTypeClass import ArabolyTypeClass

class ArabolyRules(ArabolyTypeClass):
    """XXX"""

    # {{{ dispatch_bid(self, context, newAuctionEnd, **params): XXX
    def dispatch_bid(self, context, newAuctionEnd, **params):
        if newAuctionEnd:
            params["newState"] = ArabolyGameState.GAME
        return {"context":context, "newAuctionEnd":newAuctionEnd, **params}
    # }}}
    # {{{ dispatch_buy(self, context, **params): XXX
    def dispatch_buy(self, context, **params):
        params["newState"] = ArabolyGameState.GAME
        return {"context":context, **params}
    # }}}
    # {{{ dispatch_dice(self, context, newField, newFieldBuyable, newFieldOwned, src, **params): XXX
    def dispatch_dice(self, context, newField, newFieldBuyable, newFieldOwned, src, **params):
        params["newState"] = context.state
        if "newPlayerBankrupt" in params:
            if "newPlayers" in params and params["newPlayers"] == []:
                params["newState"] = ArabolyGameState.ATTRACT
        elif context.board[newField]["type"] == ArabolyGameField.PROPERTY   \
        or context.board[newField]["type"] == ArabolyGameField.UTILITY:
            if not newFieldOwned:
                if not newFieldBuyable:
                    params["newState"] = ArabolyGameState.AUCTION
                else:
                    params["newState"] = ArabolyGameState.PROPERTY
        return {"context":context, "newField":newField, "newFieldBuyable":newFieldBuyable, "newFieldOwned":newFieldOwned, "src":src, **params}
    # }}}
    # {{{ dispatch_join(self, context, **params): XXX
    def dispatch_join(self, context, **params):
        if (len(context.players) + len(params["newPlayers"])) == context.playersMax:
            params["newState"] = ArabolyGameState.GAME
        else:
            params["newState"] = context.state
        return {"context":context, **params}
    # }}}
    # {{{ dispatch_kick(self, context, **params): XXX
    def dispatch_kick(self, context, **params):
        if len(context.players) <= 1:
            params["newState"] = ArabolyGameState.ATTRACT
        else:
            params["newState"] = context.state
        return {"context":context, **params}
    # }}}
    # {{{ dispatch_part(self, context, **params): XXX
    def dispatch_part(self, context, **params):
        if len(context.players) <= 1:
            params["newState"] = ArabolyGameState.ATTRACT
        else:
            params["newState"] = context.state
        return {"context":context,  **params}
    # }}}
    # {{{ dispatch_pass(self, context, **params): XXX
    def dispatch_pass(self, context, **params):
        if context.state == ArabolyGameState.PROPERTY:
            params["newState"] = ArabolyGameState.AUCTION
        elif context.state == ArabolyGameState.AUCTION:
            if params["newAuctionEnd"]:
                params["newState"] = ArabolyGameState.GAME
        return {"context":context, **params}
    # }}}
    # {{{ dispatch_start(self, context, **params): XXX
    def dispatch_start(self, context, **params):
        params["newState"] = ArabolyGameState.SETUP
        return {"context":context, **params}
    # }}}
    # {{{ dispatch_stop(self, context, **params): XXX
    def dispatch_stop(self, context, **params):
        params["newState"] = ArabolyGameState.ATTRACT
        return {"context":context, **params}
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120
