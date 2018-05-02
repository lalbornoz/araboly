#!/usr/bin/env python3
#
# Araboly NT 3.1 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from ArabolyGame import ArabolyGameField, ArabolyPropSubType, ArabolyGameState
from ArabolyLog import ArabolyLogLevel
from ArabolyRtl import ArabolyAlignedReplace, ArabolyRandom
from ArabolyTypeClass import ArabolyTypeClass
import time

class ArabolyOutput(ArabolyTypeClass):
    """XXX"""

    # {{{ dispatch_accept(self, channel, output, tradeState, **params): XXX
    def dispatch_accept(self, channel, output, tradeState, **params):
        delay = 0
        if tradeState["offerType"] == "buy":
            if tradeState["counter"]:
                output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "{}: Yay! {} accepts your counter-offer to sell {} at ${}!".format(tradeState["src"], tradeState["otherPlayer"], tradeState["title"], tradeState["price"])]}]
                propTo = tradeState["otherPlayer"]
            else:
                output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "{}: Yay! {} accepts your offer to buy {} at ${}!".format(tradeState["src"], tradeState["otherPlayer"], tradeState["title"], tradeState["price"])]}]
                propTo = tradeState["src"]
        elif tradeState["offerType"] == "sell":
            if tradeState["counter"]:
                output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "{}: Yay! {} accepts your counter-offer to buy {} at ${}!".format(tradeState["src"], tradeState["otherPlayer"], tradeState["title"], tradeState["price"])]}]
                propTo = tradeState["src"]
            else:
                output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "{}: Yay! {} accepts your offer to sell {} at ${}!".format(tradeState["src"], tradeState["otherPlayer"], tradeState["title"], tradeState["price"])]}]
                propTo = tradeState["otherPlayer"]
        delay += 0.900
        output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "Awfom! {} buys {} for ${}!".format(propTo, tradeState["title"], tradeState["price"])]}]
        return {"channel":channel, "output":output, "tradeState":tradeState, **params}
    # }}}
    # {{{ dispatch_bid(self, channel, context, newAuctionBids, newHighestBid, newHighestBidder, output, price, src, **params): XXX
    def dispatch_bid(self, channel, context, newAuctionBids, newHighestBid, newHighestBidder, output, price, src, **params):
        delay = 0
        output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "{} bids ${} on {}!".format(src, price, context.board[context.auctionProperty["field"]]["title"])]}]
        if params["newAuctionEnd"]:
            delay += 0.900
            output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "Awfom! {} wins the auction and buys {} for ${}!".format(newHighestBidder, context.board[context.auctionProperty["field"]]["title"], newHighestBid)]}]
            delay += 0.900
            output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "{}: roll the dice!".format(context.players[params["newPlayerCur"]])]}]
        else:
            for player in params["delAuctionBids"] if "delAuctionBids" in params else []:
                delay += 0.900
                output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "{}: you have been outbid by {}! Place bid above ${} or pass!".format(player, src, newHighestBid)]}]
            delay += 0.900
            output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "Current highest bid: {} at ${}".format(newHighestBidder, newHighestBid)]}]
            auctionBids = {**newAuctionBids, **context.auctionBids}
            if "delAuctionBids" in params:
                auctionBids = {k:auctionBids[k] for k in auctionBids if k not in params["delAuctionBids"]}
            auctionBidsLeft = [player for player in context.players if player not in auctionBids]
            delay += 0.900
            output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "Potential bidders remaining: {}".format(", ".join(auctionBidsLeft))]}]
        params["newInhibitUntil"] = time.time() + delay
        return {"channel":channel, "context":context, "newAuctionBids":newAuctionBids, "newHighestBid":newHighestBid, "newHighestBidder":newHighestBidder, "output":output, "price":price, "src":src, **params}
    # }}}
    # {{{ dispatch_board(self, channel, context, src, output, **params): XXX
    def dispatch_board(self, channel, context, src, output, **params):
        field = params["newField"] if "newField" in params else context.fields[src];
        for fieldMin, fieldMax, fieldBoardLines in context.boardFields:
            if field >= fieldMin and field <= fieldMax:
                for boardLine in fieldBoardLines:
                    boardPatterns = ["< CURRENT FIELD TITLE1 >", "< CURRENT FIELD TITLE2 >"]
                    if  boardLine.find(boardPatterns[0])    \
                    and boardLine.find(boardPatterns[1]):
                        boardLine = ArabolyAlignedReplace(boardLine, boardPatterns, context.board[field]["title"])
                    boardPatterns = ["< PLAYER NAME HERE >"]
                    if  boardLine.find(boardPatterns[0]):
                        boardLine = ArabolyAlignedReplace(boardLine, boardPatterns, src)
                    output += [{"type":"message", "delay":0, "logLevel":ArabolyLogLevel.LOG_DEBUG, "cmd":"PRIVMSG", "args":[channel, boardLine]}]
                return {"channel":channel, "context":context, "src":src, "output":output, **params}
        raise ValueError
    # }}}
    # {{{ dispatch_buy(self, channel, context, output, src, **params): XXX
    def dispatch_buy(self, channel, context, output, src, **params):
        delay = 0
        for buyString in context.boardStrings[context.fields[src]][ArabolyPropSubType.BUY][1][0]:
            rands = [ArabolyRandom(limit=150-5, min=5) for x in range(10)]
            delay += 0.900
            output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, buyString.format(owner=src, prop=context.board[context.fields[src]]["title"], rands=rands)]}]
        delay += 0.900
        output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "{}: roll the dice!".format(context.players[params["newPlayerCur"]])]}]
        params["newInhibitUntil"] = time.time() + delay
        return {"channel":channel, "context":context, "output":output, "src":src, **params}
    # }}}
    # {{{ dispatch_cheat(self, channel, cheatChance, cheatFlag, context, output, src, **params): XXX
    def dispatch_cheat(self, channel, cheatChance, cheatFlag, context, output, src, **params):
        delay = 0
        if cheatFlag:
            output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "AWFOM! {} cheats the system and gains ${}!".format(src, int(cheatChance * 66.666))]}]
        else:
            output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "OH NO! {} tried to cheat, got caught, and loses ${}!".format(src, int(cheatChance * 6.666))]}]
            if "newPlayerBankrupt" in params:
                delay += 0.900
                output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "Oh no! {} has gone bankrupt!".format(src)]}]
                for playerProp in context.properties[src]:
                    delay += 0.900
                    output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "Oops! {} is returned to the bank!".format(playerProp["title"])]}]
                delay += 0.900
                output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "Player {} parts Araboly game!".format(src)]}]
                if "newPlayers" in params and params["newPlayers"] == []:
                    delay += 0.900
                    output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "Oh no! Someone won but arab can't be arsed to write corresponding message strings!"]}]
                    delay += 0.900
                    output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "Stopping current Araboly game!"]}]
                    return {"channel":channel, "cheatChance":cheatChance, "cheatFlag":cheatFlag, "context":context, "output":output, "src":src, **params}
        return {"channel":channel, "cheatChance":cheatChance, "cheatFlag":cheatFlag, "context":context, "output":output, "src":src, **params}
    # }}}
    # {{{ dispatch_develop(self, channel, context, devCost, newDevelopedProperties, output, src, **params): XXX
    def dispatch_develop(self, channel, context, devCost, newDevelopedProperties, output, src, **params):
        delay = 0
        for newDevProp in newDevelopedProperties:
            if len(newDevelopedProperties) > 1:
                for developString in context.boardStrings[newDevProp["field"]][ArabolyPropSubType.BUY][newDevProp["level"] - 1][newDevProp["houses"][newDevProp["level"] - 1]]:
                    rands = [ArabolyRandom(limit=150-5, min=5) for x in range(10)]
                    delay += 0.900
                    output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, developString.format(owner=src, prop=context.board[newDevProp["field"]]["title"], rands=rands)]}]
                for levelString in context.boardStrings[newDevProp["field"]][ArabolyPropSubType.LEVEL][newDevProp["level"] - 1][newDevProp["houses"][newDevProp["level"] - 1]]:
                    rands = [ArabolyRandom(limit=150-5, min=5) for x in range(10)]
                    delay += 0.900
                    output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, levelString.format(owner=src, rands=rands)]}]
            else:
                for developString in context.boardStrings[newDevProp["field"]][ArabolyPropSubType.BUY][newDevProp["level"]][newDevProp["houses"][newDevProp["level"]]]:
                    rands = [ArabolyRandom(limit=150-5, min=5) for x in range(10)]
                    delay += 0.900
                    output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, developString.format(owner=src, prop=context.board[newDevProp["field"]]["title"], rands=rands)]}]
        delay += 0.900
        output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "{} pays ${} to the bank for development costs!".format(src, devCost)]}]
        params["newInhibitUntil"] = time.time() + delay
        return {"channel":channel, "context":context, "devCost":devCost, "newDevelopedProperties":newDevelopedProperties, "output":output, "src":src, **params}
    # }}}
    # {{{ dispatch_dice(self, channel, context, dice, newField, newFieldBuyable, newFieldOwned, newFieldPastGo, newPlayerCur, output, src, **params): XXX
    def dispatch_dice(self, channel, context, dice, newField, newFieldBuyable, newFieldOwned, newFieldPastGo, newPlayerCur, output, src, **params):
        cancelTradeOutput = []; pendingBuyOffers = []; pendingSellOffers = [];
        for tradeKey in context.tradeDict:
            tradeState = context.tradeDict[tradeKey]
            if tradeKey.startswith(src + "\0")                              \
            or tradeKey.endswith("\0" + src):
                if tradeState["offerType"] == "buy":
                    if tradeState["counter"]:
                        pendingBuyOffers += ["{} (counter) from {} to {} for ${}".format(tradeState["title"], tradeState["src"], tradeState["otherPlayer"], tradeState["price"])]
                    else:
                        pendingBuyOffers += ["{} from {} to {} for ${}".format(tradeState["title"], tradeState["src"], tradeState["otherPlayer"], tradeState["price"])]
                elif tradeState["offerType"] == "sell":
                    if tradeState["counter"]:
                        pendingSellOffers += ["{} (counter) from {} to {} for ${}".format(tradeState["title"], tradeState["src"], tradeState["otherPlayer"], tradeState["price"])]
                    else:
                        pendingSellOffers += ["{} from {} to {} for ${}".format(tradeState["title"], tradeState["src"], tradeState["otherPlayer"], tradeState["price"])]
        if len(pendingBuyOffers):
            cancelTradeOutput += ["Cancelling outstanding buy offers: {}".format(", ".join(pendingBuyOffers))]
        if len(pendingSellOffers):
            cancelTradeOutput += ["Cancelling outstanding sell offers: {}".format(", ".join(pendingBuyOffers))]
        if len(cancelTradeOutput):
            delay = 0
            for msg in cancelTradeOutput:
                delay += 0.900
                output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, msg]}]
        else:
            delay = 0
        output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "{} rolls {} and {}!".format(src, dice[0], dice[1])]}]
        params = self.dispatch_board(channel, context, src, output, **{"newField":newField, **params})
        if newFieldPastGo:
            delay += 0.900
            output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "Yay! {} passes past GO and collects $200!".format(src)]}]
        delay += 0.900
        output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "{} lands on {}!".format(src, context.board[newField]["title"])]}]
        if "newPlayerBankrupt" in params:
            delay += 0.900
            output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "Oh no! {} has gone bankrupt!".format(src)]}]
            for playerProp in context.properties[src]:
                delay += 0.900
                output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "Oops! {} is returned to the bank!".format(playerProp["title"])]}]
            delay += 0.900
            output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "Player {} parts Araboly game!".format(src)]}]
            if "newPlayers" in params and params["newPlayers"] == []:
                delay += 0.900
                output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "Oh no! Someone won but arab can't be arsed to write corresponding message strings!"]}]
                delay += 0.900
                output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "Stopping current Araboly game!"]}]
                return {"channel":channel, "context":context, "dice":dice, "output":output, "newField":newField, "newFieldBuyable":newFieldBuyable, "newFieldOwned":newFieldOwned, "newFieldPastGo":newFieldPastGo, "newPlayerCur":newPlayerCur, "src":src, **params}
        elif context.board[newField]["type"] == ArabolyGameField.TAX:
            delay += 0.900
            output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "Oh no! {} must pay ${}!".format(src, context.board[newField]["price"])]}]
        elif context.board[newField]["type"] == ArabolyGameField.PROPERTY   \
        or   context.board[newField]["type"] == ArabolyGameField.UTILITY:
            if not newFieldOwned:
                if not newFieldBuyable:
                    delay += 0.900
                    output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "{}: you don't have enough money to buy property {}!".format(src, context.board[newField]["title"])]}]
                    delay += 0.900
                    output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "Entering auction mode!"]}]
                else:
                    delay += 0.900
                    output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "{}: buy property {}?".format(src, context.board[newField]["title"])]}]
            else:
                if not params["newFieldOwnedSelf"]:
                    propOwner = None
                    for player in context.properties:
                        for playerProp in context.properties[player]:
                            if playerProp["field"] == newField:
                                propOwner = player; break;
                        if propOwner != None:
                            break
                    if playerProp["mortgaged"]:
                        delay += 0.900
                        output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "Oops! {} cannot collect rent on {} as it is mortgaged!".format(propOwner, context.board[newField]["title"])]}]
                    else:
                        for rentString in context.boardStrings[newField][ArabolyPropSubType.RENT][playerProp["level"]][playerProp["houses"][playerProp["level"]]]:
                            rands = [ArabolyRandom(limit=150-5, min=5) for x in range(10)]
                            delay += 0.900
                            output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, rentString.format(cost=params["newPropRent"], owner=propOwner, prop=context.board[newField]["title"], rands=rands, who=src)]}]
        if newPlayerCur != context.playerCur:
            delay += 0.900
            output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "{}: roll the dice!".format(context.players[newPlayerCur])]}]
        params["newInhibitUntil"] = time.time() + delay
        return {"channel":channel, "context":context, "dice":dice, "output":output, "newField":newField, "newFieldBuyable":newFieldBuyable, "newFieldOwned":newFieldOwned, "newFieldPastGo":newFieldPastGo, "newPlayerCur":newPlayerCur, "src":src, **params}
    # }}}
    # {{{ dispatch_help(self, channel, output, **params): XXX
    def dispatch_help(self, channel, output, **params):
        for helpLine in self.helpLines:
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, helpLine]}]
        return {"channel":channel, "output":output, **params}
    # }}}
    # {{{ dispatch_join(self, channel, context, output, src, **params): XXX
    def dispatch_join(self, channel, context, output, src, **params):
        delay = 0
        output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "Player {} joins Araboly game!".format(src)]}]
        if (len(context.players) + len(params["newPlayers"])) == context.playersMax:
            delay += 0.900
            output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "Araboly game with {} players has started!".format(context.playersMax)]}]
            delay += 0.900
            output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "{}: roll the dice!".format([*context.players, *params["newPlayers"]][context.playerCur])]}]
        params["newInhibitUntil"] = time.time() + delay
        return {"channel":channel, "context":context, "output":output, "src":src, **params}
    # }}}
    # {{{ dispatch_kick(self, channel, context, otherPlayer, output, **params): XXX
    def dispatch_kick(self, channel, context, otherPlayer, output, **params):
        delay = 0
        output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "Kicking {} from current Araboly game!".format(otherPlayer)]}]
        if len(context.players) <= 1:
            delay += 0.900
            output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "Stopping current Araboly game!"]}]
        params["newInhibitUntil"] = time.time() + delay
        return {"channel":channel, "context":context, "otherPlayer":otherPlayer, "output":output, **params}
    # }}}
    # {{{ dispatch_offer(self, channel, output, tradeState, **params): XXX
    def dispatch_offer(self, channel, output, tradeState, **params):
        delay = 0
        if tradeState["offerType"] == "buy":
            if tradeState["counter"]:
                output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "{}: {} counter-offers to sell {} to you at ${}! Accept, counter-offer, or reject?".format(tradeState["otherPlayer"], tradeState["src"], tradeState["title"], tradeState["price"])]}]
            else:
                output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "{}: {} offers to buy {} from you at ${}! Accept, counter-offer, or reject?".format(tradeState["otherPlayer"], tradeState["src"], tradeState["title"], tradeState["price"])]}]
        elif tradeState["offerType"] == "sell":
            if tradeState["counter"]:
                output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "{}: {} counter-offers to buy {} from you at ${}! Accept, counter-offer, or reject?".format(tradeState["otherPlayer"], tradeState["src"], tradeState["title"], tradeState["price"])]}]
            else:
                output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "{}: {} offers to sell {} to you at ${}! Accept, counter-offer, or reject?".format(tradeState["otherPlayer"], tradeState["src"], tradeState["title"], tradeState["price"])]}]
        return {"channel":channel, "output":output, "tradeState":tradeState, **params}
    # }}}
    # {{{ dispatch_lift(self, channel, context, field, output, src, **params): XXX
    def dispatch_lift(self, channel, context, field, output, src, **params):
        delay = 0
        mortgageCost = int(context.board[field]["price"] / 2)
        mortgageCost = int(mortgageCost + (mortgageCost * 0.10))
        output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "Awfom! {} lifts the mortgage on {} and pays ${} to the bank!".format(src, context.board[field]["title"], mortgageCost)]}]
        delay += 0.900
        output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "Yay! {} is now able to collect rent from and develop on {}!".format(src, context.board[field]["title"])]}]
        return {"channel":channel, "context":context, "field":field, "output":output, "src":src, **params}
    # }}}
    # {{{ dispatch_melp(self, context, channel, output, **params): XXX
    def dispatch_melp(self, context, channel, output, **params):
        for explosionLine in context.explosion:
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, explosionLine]}]
        output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "\u0001ACTION explodes.\u0001"]}]
        return {"context":context, "channel":channel, "output":output, **params}
    # }}}
    # {{{ dispatch_mortgage(self, channel, context, field, output, src, **params): XXX
    def dispatch_mortgage(self, channel, context, field, output, src, **params):
        delay = 0
        mortgageCost = int(context.board[field]["price"] / 2)
        output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "Oops! {} mortgages {} and receives ${} from the bank!".format(src, context.board[field]["title"], mortgageCost)]}]
        delay += 0.900
        output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "Oh no! {} is no longer able to collect rent from or develop on {}!".format(src, context.board[field]["title"])]}]
        return {"channel":channel, "context":context, "field":field, "output":output, "src":src, **params}
    # }}}
    # {{{ dispatch_part(self, channel, context, output, src, **params): XXX
    def dispatch_part(self, channel, context, output, src, **params):
        delay = 0
        output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "Player {} parts Araboly game!".format(src)]}]
        if len(context.players) <= 1:
            delay += 0.900
            output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "Stopping current Araboly game!"]}]
        params["newInhibitUntil"] = time.time() + delay
        return {"channel":channel, "context":context, "output":output, "src":src, **params}
    # }}}
    # {{{ dispatch_pass(self, channel, context, output, src, **params): XXX
    def dispatch_pass(self, channel, context, output, src, **params):
        delay = 0
        if context.state == ArabolyGameState.PROPERTY:
            delay += 0.900
            output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "The bank auctions off {} (market price: ${})!".format(context.board[context.fields[src]]["title"], context.board[context.fields[src]]["price"])]}]
            delay += 0.900
            output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "Entering auction mode!"]}]
        elif context.state == ArabolyGameState.AUCTION:
            newHighestBid = params["newHighestBid"]; newHighestBidder = params["newHighestBidder"];
            delay += 0.900
            output += [{"type":"message", "delay":0.900, "cmd":"PRIVMSG", "args":[channel, "{} leaves auction for {}!".format(src, context.board[context.auctionProperty["field"]]["title"])]}]
            if newHighestBid != 0:
                if params["newAuctionEnd"]:
                    delay += 0.900
                    output += [{"type":"message", "delay":0.900, "cmd":"PRIVMSG", "args":[channel, "{} buys {} for ${}!".format(newHighestBidder, context.board[context.auctionProperty["field"]]["title"], newHighestBid)]}]
                    delay += 0.900
                    output += [{"type":"message", "delay":0.900, "cmd":"PRIVMSG", "args":[channel, "{}: roll the dice!".format(context.players[params["newPlayerCur"]])]}]
                else:
                    delay += 0.900
                    output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "Current highest bid: {} at ${}".format(newHighestBidder, newHighestBid)]}]
                    auctionBids = {**params["newAuctionBids"], **context.auctionBids}
                    if "delAuctionBids" in params:
                        auctionBids = {k:auctionBids[k] for k in auctionBids if k not in params["delAuctionBids"]}
                    auctionBidsLeft = [player for player in context.players if player not in auctionBids]
                    delay += 0.900
                    output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "Potential bidders remaining: {}".format(", ".join(auctionBidsLeft))]}]
            else:
                if params["newAuctionEnd"]:
                    delay += 0.900
                    output += [{"type":"message", "delay":0.900, "cmd":"PRIVMSG", "args":[channel, "The bank retains {}!".format(context.board[context.auctionProperty["field"]]["title"])]}]
                    delay += 0.900
                    output += [{"type":"message", "delay":0.900, "cmd":"PRIVMSG", "args":[channel, "{}: roll the dice!".format(context.players[params["newPlayerCur"]])]}]
                else:
                    delay += 0.900
                    output += [{"type":"message", "delay":0.900, "cmd":"PRIVMSG", "args":[channel, "No bids have been placed yet!"]}]
        params["newInhibitUntil"] = time.time() + delay
        return {"channel":channel, "context":context, "output":output, "src":src, **params}
    # }}}
    # {{{ dispatch_reject(self, channel, output, tradeState, **params): XXX
    def dispatch_reject(self, channel, output, tradeState, **params):
        delay = 0
        if tradeState["offerType"] == "buy":
            if tradeState["counter"]:
                output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "{}: Oh no! {} rejects your counter-offer to sell {} at ${}!".format(tradeState["src"], tradeState["otherPlayer"], tradeState["title"], tradeState["price"])]}]
            else:
                output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "{}: Oh no! {} rejects your offer to buy {} at ${}!".format(tradeState["src"], tradeState["otherPlayer"], tradeState["title"], tradeState["price"])]}]
        elif tradeState["offerType"] == "sell":
            if tradeState["counter"]:
                output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "{}: Oh no! {} rejects your counter-offer to buy {} at ${}!".format(tradeState["src"], tradeState["otherPlayer"], tradeState["title"], tradeState["price"])]}]
            else:
                output += [{"type":"message", "delay":delay, "cmd":"PRIVMSG", "args":[channel, "{}: Oh no! {} rejects your offer to sell {} at ${}!".format(tradeState["src"], tradeState["otherPlayer"], tradeState["title"], tradeState["price"])]}]
        return {"channel":channel, "output":output, "tradeState":tradeState, **params}
    # }}}
    # {{{ dispatch_start(self, channel, context, output, players, src, **params): XXX
    def dispatch_start(self, channel, context, output, players, src, **params):
        output += [{"type":"message", "delay":0.900, "cmd":"PRIVMSG", "args":[channel, "Starting Araboly game with {} players!".format(players)]}]
        params["newInhibitUntil"] = time.time() + 0.900
        return {"channel":channel, "context":context, "output":output, "players":players, "src":src, **params}
    # }}}
    # {{{ dispatch_status(self, channel, context, output, src, **params): XXX
    def dispatch_status(self, channel, context, output, src, **params):
        if context.state == ArabolyGameState.GAME       \
        or context.state == ArabolyGameState.PROPERTY   \
        or context.state == ArabolyGameState.AUCTION:
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Araboly status for player {}:".format(src)]}]
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Field....: {}".format(context.board[context.fields[src]]["title"])]}]
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Wallet...: {}".format(context.wallets[src])]}]
            if len(context.properties[src]):
                output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Properties owned:"]}]
                for prop in context.properties[src]:
                    houses = []
                    for houseLevel in range(1, prop["level"]+1):
                        houseNumMin = 0 if prop["level"] < 2 else 1
                        for houseNum in range(houseNumMin, prop["houses"][prop["level"]]+1):
                            houses += context.boardStrings[prop["field"]][ArabolyPropSubType.HOUSE][houseLevel][houseNum]
                    if prop["mortgaged"]:
                        if len(houses):
                            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "\u0003{:02d}${} (\u001fMORTGAGED\u001f) (#{}) -- {}, developments: {}".format(prop["colourMiRC"], prop["price"], prop["field"], prop["title"], ", ".join(houses))]}]
                        else:
                            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "\u0003{:02d}${} (\u001fMORTGAGED\u001f) (#{}) -- {}".format(prop["colourMiRC"], prop["price"], prop["field"], prop["title"])]}]
                    else:
                        if len(houses):
                            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "\u0003{:02d}${} (#{}) -- {}, developments: {}".format(prop["colourMiRC"], prop["price"], prop["field"], prop["title"], ", ".join(houses))]}]
                        else:
                            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "\u0003{:02d}${} (#{}) -- {}".format(prop["colourMiRC"], prop["price"], prop["field"], prop["title"])]}]
            myPendingBuyOffers = []; myPendingSellOffers = [];
            otherPendingBuyOffers = []; otherPendingSellOffers = [];
            for tradeKey in context.tradeDict:
                tradeState = context.tradeDict[tradeKey]
                if tradeKey.startswith(src + "\0"):
                    fromSrc = True
                elif tradeKey.endswith("\0" + src):
                    fromSrc = False
                else:
                    continue
                if tradeState["offerType"] == "buy":
                    if tradeState["counter"]:
                        if fromSrc:
                            myPendingBuyOffers += ["{} (counter) from {} for ${}".format(tradeState["title"], tradeState["otherPlayer"], tradeState["price"])]
                        else:
                            otherPendingBuyOffers += ["{} (counter) from {} for ${}".format(tradeState["title"], tradeState["src"], tradeState["price"])]
                    else:
                        if fromSrc:
                            myPendingBuyOffers += ["{} from {} for ${}".format(tradeState["title"], tradeState["otherPlayer"], tradeState["price"])]
                        else:
                            otherPendingBuyOffers += ["{} from {} for ${}".format(tradeState["title"], tradeState["src"], tradeState["price"])]
                elif tradeState["offerType"] == "sell":
                    if tradeState["counter"]:
                        if fromSrc:
                            myPendingSellOffers += ["{} (counter) to {} for ${}".format(tradeState["title"], tradeState["otherPlayer"], tradeState["price"])]
                        else:
                            otherPendingSellOffers += ["{} (counter) from {} for ${}".format(tradeState["title"], tradeState["src"], tradeState["price"])]
                    else:
                        if fromSrc:
                            myPendingSellOffers += ["{} to {} for ${}".format(tradeState["title"], tradeState["otherPlayer"], tradeState["price"])]
                        else:
                            otherPendingSellOffers += ["{} from {} for ${}".format(tradeState["title"], tradeState["src"], tradeState["price"])]
            if len(myPendingBuyOffers):
                output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "My pending buy offers: {}".format(", ".join(myPendingBuyOffers))]}]
            if len(myPendingSellOffers):
                output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "My pending sell offers: {}".format(", ".join(myPendingSellOffers))]}]
            if len(otherPendingBuyOffers):
                output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Pending buy offers to me: {}".format(", ".join(otherPendingBuyOffers))]}]
            if len(otherPendingSellOffers):
                output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Pending sell offers to me: {}".format(", ".join(otherPendingSellOffers))]}]
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Current field for {}: {}".format(src, context.fields[src])]}]
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Current turn: {}".format(context.players[context.playerCur])]}]
        return {"channel":channel, "context":context, "output":output, "src":src, **params}
    # }}}
    # {{{ dispatch_stop(self, channel output, **params): XXX
    def dispatch_stop(self, channel, output, **params):
        output += [{"type":"message", "delay":0.900, "cmd":"PRIVMSG", "args":[channel, "Stopping current Araboly game!"]}]
        return {"channel":channel, "output":output, **params}
    # }}}
    # {{{ __init__(self, **kwargs): initialisation method
    def __init__(self, **kwargs):
        with open("assets/ArabolyIrcBot.hlp", "r") as fileObject:
            self.helpLines = fileObject.readlines()
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120
