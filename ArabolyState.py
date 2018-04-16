#!/usr/bin/env python3
#
# Araboly NT 3.1 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from ArabolyGame import ArabolyGameField, ArabolyGameState
from ArabolyTypeClass import ArabolyTypeClass

class ArabolyState(ArabolyTypeClass):
    """XXX"""

    # {{{ dispatch_bid(self, context, newAuctionEnd, price, src, **params): XXX
    def dispatch_bid(self, context, newAuctionEnd, price, src, **params):
        params["newAuctionBidders"] = context.auctionBidders + 1
        params["newAuctionBids"] = {src:price}
        highestBid, highestBidder = self._highestBid(context, params)
        params["newHighestBid"] = highestBid; params["newHighestBidder"] = highestBidder;
        if newAuctionEnd:
            params["delAuctionBids"] = {**context.auctionBids, **params["newAuctionBids"]}.keys()
            params["newAuctionBidders"] = -1
            params["newPlayerCur"] = (context.playerCur + 1) % len(context.players)
            params["newProperties"] = {highestBidder:[*context.properties[highestBidder], context.auctionProperty]}
            params["newWallets"] = {highestBidder:context.wallets[highestBidder] - highestBid}
        return {"context":context, "price":price, "newAuctionEnd":newAuctionEnd, "src":src, **params}
    # }}}
    # {{{ dispatch_buy(self, context, src, **params): XXX
    def dispatch_buy(self, context, src, **params):
        params["newPlayerCur"] = (context.playerCur + 1) % len(context.players)
        params["newProperties"] = {src:[*context.properties[src], {"field":context.fields[src], **context.board[context.fields[src]]}]}
        params["newWallets"] = {src:context.wallets[src] - context.board[context.fields[src]]["price"]}
        return {"context":context, "src":src, **params}
    # }}}
    # {{{ dispatch_develop(self, context, newDevelopedProperties, src, **params): XXX
    def dispatch_develop(self, context, newDevelopedProperties, src, **params):
        for newDevProp in newDevelopedProperties:
            if len(newDevelopedProperties) > 1:
                newDevProp["houses"][newDevProp["level"]] = 3
                newDevProp["level"] += 1
            else:
                newDevProp["houses"][newDevProp["level"]] += 1
        return {"context":context, "newDevelopedProperties":newDevelopedProperties, "src":src, **params}
    # }}}
    # {{{ dispatch_dice(self, context, newField, newFieldBuyable, newFieldOwned, newFieldPastGo, src, **params): XXX
    def dispatch_dice(self, context, newField, newFieldBuyable, newFieldOwned, newFieldPastGo, src, **params):
        params["newPlayerCur"] = context.playerCur; params["newWallets"] = {};
        if newFieldPastGo:
            params["newPlayerCur"] = (context.playerCur + 1) % len(context.players)
            params["newWallets"] = {src:context.wallets[src] + 200}
        if context.board[newField]["type"] == ArabolyGameField.PROPERTY \
        or context.board[newField]["type"] == ArabolyGameField.UTILITY:
            if not newFieldOwned:
                if not newFieldBuyable:
                    params["newAuctionBidders"] = 0
                    params["newAuctionProperty"] = {"field":newField, **context.board[newField]}
            else:
                params["newPlayerCur"] = (context.playerCur + 1) % len(context.players)
                if not params["newFieldOwnedSelf"]:
                    for player in context.properties:
                        for playerProp in context.properties[player]:
                            if playerProp["field"] == newField:
                                propOwner = player
                    params["newWallets"] = {src:context.wallets[src] - params["newPropRent"], propOwner:context.wallets[propOwner] + params["newPropRent"]}
                    if params["newWallets"][src] <= 0:
                        params["newPlayerBankrupt"] = True
                        return self._dispatch_remove(**{"context":context, "newField":newField, "newFieldBuyable":newFieldBuyable, "newFieldOwned":newFieldOwned, "newFieldPastGo":newFieldPastGo, "src":src, **params})
        elif context.board[newField]["type"] == ArabolyGameField.TAX:
            params["newPlayerCur"] = (context.playerCur + 1) % len(context.players)
            params["newWallets"] = {src:context.wallets[src] - context.board[newField]["price"]}
            if params["newWallets"][src] <= 0:
                params["newPlayerBankrupt"] = True
                return self._dispatch_remove(**{"context":context, "newField":newField, "newFieldBuyable":newFieldBuyable, "newFieldOwned":newFieldOwned, "newFieldPastGo":newFieldPastGo, "src":src, **params})
        else:
            params["newPlayerCur"] = (context.playerCur + 1) % len(context.players)
        return {"context":context, "newField":newField, "newFieldBuyable":newFieldBuyable, "newFieldOwned":newFieldOwned, "newFieldPastGo":newFieldPastGo, "src":src, **params}
    # }}}
    # {{{ dispatch_join(self, context, src, **params): XXX
    def dispatch_join(self, context, src, **params):
        params["newFields"] = {src:0}
        params["newPlayers"] = [src]
        params["newProperties"] = {src:[]}
        params["newWallets"] = {src:1500}
        return {"context":context, "src":src, **params}
    # }}}
    # {{{ dispatch_kick(self, **params): XXX
    def dispatch_kick(self, **params):
        return self._dispatch_remove(**params)
    # }}}
    # {{{ dispatch_part(self, **params): XXX
    def dispatch_part(self, **params):
        return self._dispatch_remove(**params)
    # }}}
    # {{{ dispatch_pass(self, context, src, **params): XXX
    def dispatch_pass(self, context, src, **params):
        if context.state == ArabolyGameState.PROPERTY:
            params["newAuctionBidders"] = 0
            params["newAuctionProperty"] = {"field":context.fields[src], **context.board[context.fields[src]]}
        elif context.state == ArabolyGameState.AUCTION:
            params["newAuctionBidders"] = context.auctionBidders + 1
            params["newAuctionBids"] = {src:0}
            highestBid, highestBidder = self._highestBid(context, params)
            params["newHighestBid"] = highestBid; params["newHighestBidder"] = highestBidder;
            if params["newAuctionEnd"]:
                params["delAuctionBids"] = {**context.auctionBids, **params["newAuctionBids"]}.keys()
                params["newAuctionBidders"] = -1
                params["newPlayerCur"] = (context.playerCur + 1) % len(context.players)
                if highestBid != 0:
                    propField = context.auctionProperty
                    params["newProperties"] = {highestBidder:[*context.properties[highestBidder], propField]}
                    params["newWallets"] = {highestBidder:context.wallets[highestBidder] - highestBid}
        return {"context":context, "src":src, **params}
    # }}}
    # {{{ dispatch_start(self, context, players, **params): XXX
    def dispatch_start(self, context, players, **params):
        params["newPlayerCur"] = 0
        params["newFields"] = {}
        params["newPlayersMax"] = int(players)
        params["newProperties"] = {}
        params["newWallets"] = {}
        return {"context":context, "players":players, **params}
    # }}}
    # {{{ dispatch_stop(self, context, **params): XXX
    def dispatch_stop(self, context, **params):
        params["newPlayerCur"] = -1
        params["newFields"] = []
        params["newPlayersMax"] = -1
        params["newProperties"] = {}
        params["newWallets"] = {}
        return {"context":context, **params}
    # }}}
    # {{{ _dispatch_remove(self, args, cmd, context, src, **params): XXX
    def _dispatch_remove(self, args, cmd, context, src, **params):
        removePlayer = args[0] if cmd == "kick" else src
        params["delPlayers"] = [removePlayer]
        if removePlayer in context.fields:
            params["delPlayerFields"] = [removePlayer]
        if removePlayer in context.wallets:
            params["delWallets"] = [removePlayer]
        params["delProperties"] = [removePlayer]
        if len(context.players) <= 2:
            params["newPlayerCur"] = -1
            params["newPlayers"] = []
            params["newPlayersMax"] = -1
        else:
            params["newPlayerCur"] = (context.playerCur + 1) % len(context.players)
        return {"args":args, "cmd":cmd, "context":context, "src":src, **params}
    # }}}
    # {{{ _highestBid(self, context, params): XXX
    def _highestBid(self, context, params):
        auctionBids = {**context.auctionBids, **params["newAuctionBids"]}
        sortedBids = sorted(auctionBids, key=auctionBids.get)
        return auctionBids[sortedBids[-1]], sortedBids[-1]
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120
