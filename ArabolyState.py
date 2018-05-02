#!/usr/bin/env python3
#
# Araboly NT 3.1 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from ArabolyGame import ArabolyGameField, ArabolyGameState
from ArabolyRtl import ArabolyRandom
from ArabolyTypeClass import ArabolyTypeClass

class ArabolyState(ArabolyTypeClass):
    """XXX"""

    # {{{ dispatch_accept(self, context, otherPlayer, src, status, tradeKey, tradeState, **params): XXX
    def dispatch_accept(self, context, otherPlayer, src, status, tradeKey, tradeState, **params):
        params["delTradeDict"] = [tradeKey]
        if tradeState["offerType"] == "buy":
            propSrc = tradeState["otherPlayer"]; propTo = tradeState["src"];
        elif tradeState["offerType"] == "sell":
            propSrc = tradeState["src"]; propTo = tradeState["otherPlayer"];
        params["newProperties"] = {}; params["newWallets"] = {};
        params["newProperties"][propSrc] = [p for p in context.properties[propSrc] if p["field"] != tradeState["field"]]
        params["newProperties"][propTo] = [*context.properties[propTo], {"field":tradeState["field"], **context.board[tradeState["field"]]}]
        params["newWallets"][propSrc] = context.wallets[propSrc] + tradeState["price"]
        params["newWallets"][propTo] = context.wallets[propTo] - tradeState["price"]
        return {"context":context, "otherPlayer":otherPlayer, "src":src, "status":status, "tradeKey":tradeKey, "tradeState":tradeState, **params}
    # }}}
    # {{{ dispatch_bid(self, context, newAuctionEnd, price, src, **params): XXX
    def dispatch_bid(self, context, newAuctionEnd, price, src, **params):
        params["delAuctionBids"] = []
        for player in context.auctionBids:
            if player != src and context.auctionBids[player] != 0:
                params["delAuctionBids"] += [player]
        params["newAuctionBids"] = {src:price}
        highestBid, highestBidder = self._highestBid(context, params)
        params["newHighestBid"] = highestBid; params["newHighestBidder"] = highestBidder;
        if newAuctionEnd:
            params["delAuctionBids"] = {**context.auctionBids, **params["newAuctionBids"]}.keys()
            params["delAuctionProperty"] = context.auctionProperty.keys()
            params["newPlayerCur"] = (context.playerCur + 1) % len(context.players)
            params["newProperties"] = {highestBidder:[*context.properties[highestBidder], context.auctionProperty.copy()]}
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
    # {{{ dispatch_cheat(self, context, src, **params): XXX
    def dispatch_cheat(self, context, src, **params):
        params["cheatChance"] = ArabolyRandom(limit=100, min=0)
        params["cheatFlag"] = params["cheatChance"] < 5
        if params["cheatFlag"]:
            params["newWallets"] = {src:context.wallets[src] + (int(params["cheatChance"] * 66.666))}
        else:
            params["newWallets"] = {src:context.wallets[src] - (int(params["cheatChance"] * 6.666))}
        if params["newWallets"][src] <= 0:
            params["newPlayerBankrupt"] = True
            return self._dispatch_remove(**{"context":context, "src":src, **params})
        return {"context":context, "src":src, **params}
    # }}}
    # {{{ dispatch_develop(self, context, newDevelopedProperties, src, **params): XXX
    def dispatch_develop(self, context, newDevelopedProperties, src, **params):
        params["devCost"] = 0
        for newDevProp in newDevelopedProperties:
            if len(newDevelopedProperties) > 1:
                newDevProp["houses"][newDevProp["level"]] = 3
                newDevProp["level"] += 1
            else:
                newDevProp["houses"][newDevProp["level"]] += 1
            params["devCost"] += int(newDevProp["price"] / 2)
        return {"context":context, "newDevelopedProperties":newDevelopedProperties, "src":src, **params}
    # }}}
    # {{{ dispatch_dice(self, context, newField, newFieldBuyable, newFieldOwned, newFieldPastGo, src, **params): XXX
    def dispatch_dice(self, context, newField, newFieldBuyable, newFieldOwned, newFieldPastGo, src, **params):
        params["delTradeDict"] = []
        for tradeKey in context.tradeDict:
            tradeState = context.tradeDict[tradeKey]
            if tradeKey.startswith(src + "\0"):
                params["delTradeDict"] += [tradeKey]
            elif tradeKey.endswith("\0" + src):
                params["delTradeDict"] += [tradeKey]
        params["newPlayerCur"] = context.playerCur; params["newWallets"] = {};
        if newFieldPastGo:
            params["newPlayerCur"] = (context.playerCur + 1) % len(context.players)
            params["newWallets"] = {src:context.wallets[src] + 200}
        if context.board[newField]["type"] == ArabolyGameField.PROPERTY \
        or context.board[newField]["type"] == ArabolyGameField.UTILITY:
            if not newFieldOwned:
                params["newPlayerCur"] = context.playerCur
                if not newFieldBuyable:
                    params["newAuctionProperty"] = {"field":newField, **context.board[newField]}
            else:
                params["newPlayerCur"] = (context.playerCur + 1) % len(context.players)
                if not params["newFieldOwnedSelf"]:
                    propOwner = None
                    for player in context.properties:
                        for playerProp in context.properties[player]:
                            if playerProp["field"] == newField:
                                propOwner = player; break;
                        if propOwner != None:
                            break
                    if not playerProp["mortgaged"]:
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
    # {{{ dispatch_lift(self, context, field, src, status, **params): XXX
    def dispatch_lift(self, context, field, src, status, **params):
        propFound = False
        for srcProp in context.properties[src]:
            if srcProp["field"] == field:
                propFound = True; break;
        if not propFound or not srcProp["mortgaged"]:
            status = False
        else:
            mortgageCost = int(srcProp["price"] / 2)
            mortgageCost = int(mortgageCost + (mortgageCost * 0.10))
            if context.wallets[src] <= mortgageCost:
                status = False
            else:
                params["newWallets"] = {src:context.wallets[src] - mortgageCost}
                srcProp["mortgaged"] = False
        return {"context":context, "field":field, "src":src, "status":status, **params}
    # }}}
    # {{{ dispatch_mortgage(self, context, field, src, status, **params): XXX
    def dispatch_mortgage(self, context, field, src, status, **params):
        propFound = False
        for srcProp in context.properties[src]:
            if srcProp["field"] == field:
                propFound = True; break;
        if not propFound or srcProp["mortgaged"]:
            status = False
        else:
            mortgageCost = int(srcProp["price"] / 2)
            params["newWallets"] = {src:context.wallets[src] + mortgageCost}
            srcProp["mortgaged"] = True
        return {"context":context, "field":field, "src":src, "status":status, **params}
    # }}}
    # {{{ dispatch_offer(self, context, field, offerType, otherPlayer, price, src, status, tradeKey, **params): XXX
    def dispatch_offer(self, context, field, offerType, otherPlayer, price, src, status, tradeKey, **params):
        if "tradeKeyOld" in params:
            counterOffer = True
            params["delTradeDict"] = [params["tradeKeyOld"]]
        else:
            counterOffer = False
        if offerType == "buy":
            offerFrom = src; offerTo = otherPlayer;
        elif offerType == "sell":
            offerFrom = otherPlayer; offerTo = src;
        if context.wallets[offerFrom] <= price:
            status = False
        else:
            propFound = False
            for otherProp in context.properties[offerTo]:
                if otherProp["field"] == field:
                    propFound = True; break;
            if not propFound:
                status = False
            else:
                params["newTradeDict"] = {tradeKey:{"counter":counterOffer, "field":field, "offerType":offerType, "price":price, "otherPlayer":otherPlayer, "src":src, "title":context.board[field]["title"]}}
                params["tradeState"] = params["newTradeDict"][tradeKey]
        return {"context":context, "field":field, "offerType":offerType, "otherPlayer":otherPlayer, "price":price, "src":src, "status":status, "tradeKey":tradeKey, **params}
    # }}}
    # {{{ dispatch_part(self, **params): XXX
    def dispatch_part(self, **params):
        return self._dispatch_remove(**params)
    # }}}
    # {{{ dispatch_pass(self, context, src, **params): XXX
    def dispatch_pass(self, context, src, **params):
        if context.state == ArabolyGameState.PROPERTY:
            params["newAuctionProperty"] = {"field":context.fields[src], **context.board[context.fields[src]]}
        elif context.state == ArabolyGameState.AUCTION:
            params["newAuctionBids"] = {src:0}
            highestBid, highestBidder = self._highestBid(context, params)
            params["newHighestBid"] = highestBid; params["newHighestBidder"] = highestBidder;
            if params["newAuctionEnd"]:
                params["delAuctionBids"] = {**context.auctionBids, **params["newAuctionBids"]}.keys()
                params["delAuctionProperty"] = context.auctionProperty.keys()
                params["newPlayerCur"] = (context.playerCur + 1) % len(context.players)
                if highestBid != 0:
                    propField = context.auctionProperty.copy()
                    params["newProperties"] = {highestBidder:[*context.properties[highestBidder], propField]}
                    params["newWallets"] = {highestBidder:context.wallets[highestBidder] - highestBid}
        return {"context":context, "src":src, **params}
    # }}}
    # {{{ dispatch_reject(self, context, otherPlayer, src, status, tradeKey, **params): XXX
    def dispatch_reject(self, context, otherPlayer, src, status, tradeKey, **params):
        params["delTradeDict"] = [tradeKey]
        params["tradeState"] = context.tradeDict[tradeKey]
        return {"context":context, "otherPlayer":otherPlayer, "src":src, "status":status, "tradeKey":tradeKey, **params}
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
        if removePlayer in context.properties:
            params["delProperties"] = [removePlayer]
        if removePlayer in context.wallets:
            params["delWallets"] = [removePlayer]
        if len(context.players) <= 2:
            params["newPlayerCur"] = -1
            params["newPlayers"] = []
            params["newPlayersMax"] = -1
        else:
            params["newPlayerCur"] = (context.playerCur + 1) % (len(context.players) - 1)
        return {"args":args, "cmd":cmd, "context":context, "src":src, **params}
    # }}}
    # {{{ _highestBid(self, context, params): XXX
    def _highestBid(self, context, params):
        auctionBids = {**context.auctionBids, **params["newAuctionBids"]}
        sortedBids = sorted(auctionBids, key=auctionBids.get)
        return auctionBids[sortedBids[-1]], sortedBids[-1]
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120
