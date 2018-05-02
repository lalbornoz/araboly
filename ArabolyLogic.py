#!/usr/bin/env python3
#
# Araboly NT 3.1 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from ArabolyGame import ArabolyGameField, ArabolyGameState
from ArabolyTypeClass import ArabolyTypeClass

class ArabolyLogic(ArabolyTypeClass):
    """XXX"""

    # {{{ dispatch_bid(self, context, price, src, status, **params): XXX
    def dispatch_bid(self, context, price, src, status, **params):
        if context.wallets[src] <= price:
            status = False
        else:
            for player in context.auctionBids:
                if context.auctionBids[player] >= price:
                    status = False
            if status:
                auctionBids = {k:context.auctionBids[k] for k in context.auctionBids if context.auctionBids[k] == 0}
                params["newAuctionEnd"] = (sorted(context.players) == sorted({src:price, **auctionBids}))
        return {"context":context, "price":price, "src":src, "status":status, **params}
    # }}}
    # {{{ dispatch_develop(self, context, field, level, src, status, **params): XXX
    def dispatch_develop(self, context, field, level, src, status, **params):
        status = False if level > 3 else True
        if status:
            status = False
            for playerProp in context.properties[src]:
                if playerProp["field"] == field:
                    if playerProp["level"] == level:
                        if context.wallets[src] >= playerProp["price"]:
                            status = True; targetField = playerProp; break;
            if status:
                if targetField["type"] != ArabolyGameField.PROPERTY:
                    status = False
        if status:
            newDevelopedProperties = []
            for boardPropNum in range(len(context.board)):
                if context.board[boardPropNum]["colour"] == playerProp["colour"]:
                    found = False
                    for playerProp in context.properties[src]:
                        if playerProp["field"] == boardPropNum:
                            found = True; break;
                    if not found:
                        status = False; break;
                    else:
                        newDevelopedProperties += [playerProp]
        if status:
            incrLevel = True
            for otherProp in newDevelopedProperties:
                if otherProp != targetField:
                    if otherProp["houses"][targetField["level"]] != 1:
                        incrLevel = False; break;
            if targetField["level"] == 3:
                incrLevel = False
            if not incrLevel:
                newDevelopedProperties = [targetField]
            params["newDevelopedProperties"] = newDevelopedProperties 
        return {"context":context, "field":field, "level":level, "src":src, "status":status, **params}
    # }}}
    # {{{ dispatch_dice(self, context, dice, src, **params): XXX
    def dispatch_dice(self, context, dice, src, **params):
        newField = (context.fields[src] + dice[0] + dice[1]) % len(context.board)
        params["newFieldBuyable"] = False
        params["newFieldOwned"] = False; params["newFieldOwnedSelf"] = False;
        params["newFieldPastGo"] = True if newField < context.fields[src] else False
        if context.board[newField]["type"] == ArabolyGameField.PROPERTY \
        or context.board[newField]["type"] == ArabolyGameField.UTILITY:
            for player in context.properties:
                for playerProp in context.properties[player]:
                    if playerProp["field"] == newField:
                        if player == src:
                            params["newFieldOwned"] = True; params["newFieldOwnedSelf"] = True;
                        else:
                            params["newFieldOwned"] = True
                            fullGroup = True
                            for boardPropNum in range(len(context.board)):
                                if context.board[boardPropNum]["colour"] == playerProp["colour"]:
                                    found = False
                                    for playerProp_ in context.properties[src]:
                                        if playerProp_["field"] == boardPropNum:
                                            found = True; break;
                                    if not found:
                                        fullGroup = False; break;
                            params["newPropRent"] = int(playerProp["price"] * 0.10)
                            if fullGroup:
                                if playerProp["houses"][playerProp["level"]] != 0:
                                    params["newPropRent"] = int(params["newPropRent"] * (2 + (0.5 * playerProp["level"])))
                                else:
                                    params["newPropRent"] *= 2
            if not params["newFieldOwned"]:
                srcWallet = context.wallets[src]
                if params["newFieldPastGo"]:
                    srcWallet += 200
                if srcWallet > context.board[newField]["price"]:
                    params["newFieldBuyable"] = True
        params["newField"] = newField
        params["newFields"] = {src:newField}
        return {"context":context, "dice":dice, "src":src, **params}
    # }}}
    # {{{ dispatch_pass(self, context, src, status, **params): XXX
    def dispatch_pass(self, context, src, status, **params):
        if context.state == ArabolyGameState.AUCTION:
            if src in context.auctionBids:
                status = False
            else:
                params["newAuctionEnd"] = (sorted(context.players) == sorted({src:0, **context.auctionBids}))
        return {"context":context, "src":src, "status":status, **params}
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120
