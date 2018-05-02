#!/usr/bin/env python3
#
# Araboly NT 3.1 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucio Andrés Illanes Albornoz <lucio@lucioillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from ArabolyGame import ArabolyGameField, ArabolyGameState
from ArabolyTypeClass import ArabolyTypeClass
from fnmatch import fnmatch

class ArabolyValidate(ArabolyTypeClass):
    """XXX"""

    # {{{ dispatch_accept(self, args, context, src, status, **params): XXX
    def dispatch_accept(self, args, context, src, status, **params):
        if context.state != ArabolyGameState.GAME       \
        or len(args) != 1                               \
        or args[0] == src or not args[0] in context.players:
            status = False
        else:
            otherPlayer = args[0]; tradeKey = otherPlayer + "\0" + src;
            if tradeKey not in context.tradeDict:
                status = False
            else:
                params.update({"otherPlayer":otherPlayer, "tradeKey":tradeKey, "tradeState":context.tradeDict[tradeKey]})
        return {"args":args, "context":context, "src":src, "status":status, **params}
    # }}}
    # {{{ dispatch_bid(self, args, context, status, **params): XXX
    def dispatch_bid(self, args, context, status, **params):
        if context.state != ArabolyGameState.AUCTION    \
        or len(args) != 1 or not args[0].isdigit()      \
        or int(args[0]) == 0:
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
    # {{{ dispatch_cheat(self, args, context, src, status, **params): XXX
    def dispatch_cheat(self, args, context, src, status, **params):
        if  context.state != ArabolyGameState.GAME          \
        and context.state != ArabolyGameState.PROPERTY      \
        and context.state != ArabolyGameState.AUCTION:
            status = False
        elif context.players[context.playerCur] != src:
            status = False
        return {"args":args, "context":context, "src":src, "status":status, **params}
    # }}}
    # {{{ dispatch_develop(self, args, context, status, **params): XXX
    def dispatch_develop(self, args, context, status, **params):
        if  context.state != ArabolyGameState.GAME                          \
        and context.state != ArabolyGameState.PROPERTY:
            status = False
        elif len(args) != 2                                                 \
        or   not args[0].isdigit() or not args[1].isdigit():
            status = False
        else:
            field = int(args[0])
            if field >= len(context.board):
                status = False
            elif context.board[field]["type"] != ArabolyGameField.PROPERTY  \
            and  context.board[field]["type"] != ArabolyGameField.UTILITY:
                status = False
            elif context.board[field]["mortgaged"]:
                status = False
            else:
                params.update({"field":field, "level":int(args[1])})
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
    # {{{ dispatch_kick(self, args, channel, context, srcFull, status, **params): XXX
    def dispatch_kick(self, args, channel, context, srcFull, status, **params):
        if context.state == ArabolyGameState.DISABLED   \
        or len(args) != 1 or len(args[0]) < 1           \
        or args[0] not in context.players:
            status = False
        else:
            params["otherPlayer"] = args[0]
            status = self._authorised(channel, context, srcFull)
        return {"args":args, "channel":channel, "context":context, "srcFull":srcFull, "status":status, **params}
    # }}}
    # {{{ dispatch_lift(self, args, context, status, **params): XXX
    def dispatch_lift(self, args, context, status, **params):
        if  context.state != ArabolyGameState.GAME      \
        and context.state != ArabolyGameState.PROPERTY:
            status = False
        elif len(args) != 1 or not args[0].isdigit():
            status = False
        else:
            field = int(args[0])
            if field >= len(context.board):
                status = False
            elif context.board[field]["type"] != ArabolyGameField.PROPERTY:
                status = False
            else:
                params.update({"field":field})
        return {"args":args, "context":context, "status":status, **params}
    # }}}
    # {{{ dispatch_mortgage(self, args, context, status, **params): XXX
    def dispatch_mortgage(self, args, context, status, **params):
        if  context.state != ArabolyGameState.GAME      \
        and context.state != ArabolyGameState.PROPERTY  \
        and context.state != ArabolyGameState.BANKRUPTCY:
            status = False
        elif len(args) != 1 or not args[0].isdigit():
            status = False
        else:
            field = int(args[0])
            if field >= len(context.board):
                status = False
            elif context.board[field]["type"] != ArabolyGameField.PROPERTY:
                status = False
            else:
                params.update({"field":field})
        return {"args":args, "context":context, "status":status, **params}
    # }}}
    # {{{ dispatch_offer(self, args, context, src, status, **params): XXX
    def dispatch_offer(self, args, context, src, status, **params):
        if context.state != ArabolyGameState.GAME                           \
        or len(args) != 4                                                   \
        or args[0] not in ["buy", "sell"]                                   \
        or args[1] == src or not args[1] in context.players                 \
        or not args[2].isdigit() or not args[3].isdigit():
            status = False
        else:
            offerType = args[0]; field = int(args[2]);
            if field >= len(context.board):
                status = False
            elif context.board[field]["type"] != ArabolyGameField.PROPERTY  \
            and  context.board[field]["type"] != ArabolyGameField.UTILITY:
                status = False
            else:
                otherPlayer = args[1]
                tradeKeyOld = otherPlayer + "\0" + src; tradeKey = src + "\0" + otherPlayer;
                if tradeKeyOld in context.tradeDict:
                    oldOfferType = context.tradeDict[tradeKeyOld]["offerType"]
                    if offerType == "buy" and oldOfferType != "sell":
                        status = False
                    elif offerType == "sell" and oldOfferType != "buy":
                        status = False
                    else:
                        params.update({"field":field, "offerType":offerType, "otherPlayer":otherPlayer, "price":int(args[3]), "tradeKey":tradeKey, "tradeKeyOld":tradeKeyOld})
                else:
                    if context.players[context.playerCur] != src            \
                    or tradeKey in context.tradeDict:
                        status = False
                    else:
                        params.update({"field":field, "offerType":offerType, "otherPlayer":otherPlayer, "price":int(args[3]), "tradeKey":tradeKey})
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
    # {{{ dispatch_reject(self, args, context, src, status, **params): XXX
    def dispatch_reject(self, args, context, src, status, **params):
        if context.state != ArabolyGameState.GAME       \
        or len(args) != 1                               \
        or args[0] == src or not args[0] in context.players:
            status = False
        else:
            otherPlayer = args[0]; tradeKey = otherPlayer + "\0" + src;
            if tradeKey not in context.tradeDict:
                status = False
            else:
                params.update({"otherPlayer":otherPlayer, "tradeKey":tradeKey, "tradeState":context.tradeDict[tradeKey]})
        return {"args":args, "context":context, "src":src, "status":status, **params}
    # }}}
    # {{{ dispatch_start(self, args, context, src, status, **params): XXX
    def dispatch_start(self, args, context, src, status, **params):
        if context.state != ArabolyGameState.ATTRACT    \
        or len(args) != 1 or not args[0].isdigit()      \
        or int(args[0]) < 2 or int(args[0]) > 6:
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
    # {{{ dispatch_stop(self, args, channel, context, srcFull, status, **params): XXX
    def dispatch_stop(self, args, channel, context, srcFull, status, **params):
        if  context.state != ArabolyGameState.SETUP     \
        and context.state != ArabolyGameState.GAME      \
        and context.state != ArabolyGameState.PROPERTY  \
        and context.state != ArabolyGameState.AUCTION:
            status = False
        elif len(args):
            status = False
        else:
            status = self._authorised(channel, context, srcFull)
        return {"args":args, "channel":channel, "context":context, "srcFull":srcFull, "status":status, **params}
    # }}}
    # {{{ _authorised(self, channel, context, srcFull): XXX
    def _authorised(self, channel, context, srcFull):
        for hostnameMask, channelMask, srcMask in context.clientUaf:
            if  fnmatch(context.clientParams["hostname"], hostnameMask) \
            and fnmatch(channel, channelMask)                           \
            and fnmatch(srcFull, srcMask):
                return True
        return False
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120
