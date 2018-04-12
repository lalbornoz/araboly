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
        params["newAuctionEnd"] = False
        if  src in context.auctionBids  \
        and context.auctionBids[src] == 0:
            status = False
        elif context.wallets[src] <= price:
            status = False
        else:
            for player in context.auctionBids:
                if context.auctionBids[player] >= price:
                    status = False
        return {"context":context, "price":price, "src":src, "status":status, **params}
    # }}}
    # {{{ dispatch_develop(self, context, field, level, src, status, **params): XXX
    def dispatch_develop(self, context, field, level, src, status, **params):
        status = False if level > 3 else True
        if status:
            status = False
            for playerProp in context.properties[src]:
                if playerProp[-1] == field:
                    if playerProp[4] == level:
                        if context.wallets[src] >= playerProp[1]:
                            status = True; targetField = playerProp; break;
            if status:
                if targetField[0] != ArabolyGameField.PROPERTY:
                    status = False
        if status:
            newDevelopedProperties = []
            for boardPropNum in range(len(context.board)):
                if context.board[boardPropNum][2] == playerProp[2]:
                    found = False
                    for playerProp in context.properties[src]:
                        if playerProp[-1] == boardPropNum:
                            found = True; break;
                    if not found:
                        status = False; break;
                    else:
                        newDevelopedProperties += [playerProp]
        if status:
            incrLevel = True
            for otherProp in newDevelopedProperties:
                if otherProp != targetField:
                    if otherProp[5][targetField[4]] != 1:
                        incrLevel = False; break;
            if targetField[4] == 3:
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
        if context.board[newField][0] == ArabolyGameField.PROPERTY  \
        or context.board[newField][0] == ArabolyGameField.UTILITY:
            for player in context.properties:
                for playerProp in context.properties[player]:
                    if playerProp[-1] == newField:
                        if player == src:
                            params["newFieldOwned"] = True; params["newFieldOwnedSelf"] = True;
                        else:
                            params["newFieldOwned"] = True; params["newPropRent"] = playerProp[1];
                            fullGroup = True
                            for boardPropNum in range(len(context.board)):
                                if context.board[boardPropNum][2] == playerProp[2]:
                                    found = False
                                    for playerProp_ in context.properties[src]:
                                        if playerProp_[-1] == boardPropNum:
                                            found = True; break;
                                    if not found:
                                        fullGroup = False; break;
                            if fullGroup:
                                if playerProp[5][playerProp[4]] > 0:
                                    params["newPropRent"] *= 2 * playerProp[5][playerProp[4]]
                                else:
                                    params["newPropRent"] *= 2
            if  not params["newFieldOwned"]                         \
            and context.wallets[src] > context.board[newField][1]:
                params["newFieldBuyable"] = True
        params["newFieldPastGo"] = True if newField < context.fields[src] else False
        params["newField"] = newField
        params["newFields"] = {src:newField}
        return {"context":context, "dice":dice, "src":src, **params}
    # }}}
    # {{{ dispatch_pass(self, context, src, status, **params): XXX
    def dispatch_pass(self, context, src, status, **params):
        if context.state == ArabolyGameState.AUCTION:
            params["newAuctionEnd"] = False
            if  src in context.auctionBids      \
            and context.auctionBids[src] == 0:
                status = False
            elif context.auctionBidders <= 2:
                auctionBidders = list(context.auctionBids)
                if src not in auctionBidders:
                    auctionBidders += [src]
                if sorted(context.players) == sorted(auctionBidders):
                    params["newAuctionEnd"] = True
        return {"context":context, "src":src, "status":status, **params}
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120
