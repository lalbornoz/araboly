#!/usr/bin/env python3
#
# Araboly NT 3.1 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucio Andrés Illanes Albornoz <lucio@lucioillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from ArabolyGame import ArabolyGameField, ArabolyGameState
from ArabolyTypeClass import ArabolyTypeClass

class ArabolyOutput(ArabolyTypeClass):
    """XXX"""
    helpLines = []

    # {{{ dispatch_bid(self, channel, context, newAuctionBids, newHighestBid, newHighestBidder, output, price, src, **params): XXX
    def dispatch_bid(self, channel, context, newAuctionBids, newHighestBid, newHighestBidder, output, price, src, **params):
        output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "{} bids ${} on {}!".format(src, price, context.board[context.auctionProperty[-1]][3])]}]
        if params["newAuctionEnd"]:
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "{} buys {} for ${}!".format(newHighestBidder, context.board[context.auctionProperty[-1]][3], newHighestBid)]}]
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "{}: roll the dice!".format(context.players[params["newPlayerCur"]])]}]
        else:
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Current highest bid: ${}".format(newHighestBid)]}]
        return {"channel":channel, "context":context, "newAuctionBids":newAuctionBids, "newHighestBid":newHighestBid, "newHighestBidder":newHighestBidder, "output":output, "price":price, "src":src, **params}
    # }}}
    # {{{ dispatch_board(self, channel, context, output, **params): XXX
    def dispatch_board(self, channel, context, output, **params):
        for boardLine in context.boardTmp:
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, boardLine]}]
        return {"channel":channel, "context":context, "output":output, **params}
    # }}}
    # {{{ dispatch_buy(self, channel, context, output, src, **params): XXX
    def dispatch_buy(self, channel, context, output, src, **params):
        output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "{} buys {} for ${}!".format(src, context.board[context.fields[src]][3], context.board[context.fields[src]][1])]}]
        output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "{}: roll the dice!".format(context.players[params["newPlayerCur"]])]}]
        return {"channel":channel, "context":context, "output":output, "src":src, **params}
    # }}}
    # {{{ dispatch_develop(self, channel, context, newDevelopedProperties, output, src, **params): XXX
    def dispatch_develop(self, channel, context, newDevelopedProperties, output, src, **params):
        for newDevProp in newDevelopedProperties:
            if len(newDevelopedProperties) > 1:
                output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "{} develops {} to {} houses!".format(src, newDevProp[3], newDevProp[5][newDevProp[4] - 1])]}]
                output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "{} develops {} to level {}!".format(src, newDevProp[3], newDevProp[4])]}]
            else:
                output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "{} develops {} to {} houses!".format(src, newDevProp[3], newDevProp[5][newDevProp[4]])]}]
        return {"channel":channel, "context":context, "newDevelopedProperties":newDevelopedProperties, "output":output, "src":src, **params}
    # }}}
    # {{{ dispatch_dice(self, channel, context, dice, newField, newFieldBuyable, newFieldOwned, newFieldPastGo, newPlayerCur, output, src, **params): XXX
    def dispatch_dice(self, channel, context, dice, newField, newFieldBuyable, newFieldOwned, newFieldPastGo, newPlayerCur, output, src, **params):
        output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "{} rolls {} and {}!".format(src, dice[0], dice[1])]}]
        for boardLine in context.boardTmp:
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, boardLine]}]
        output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "{} lands on {}!".format(src, context.board[newField][3])]}]
        if newFieldPastGo:
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "{} collects 200!".format(src)]}]
        if "newPlayerBankrupt" in params:
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Oh no! {} has gone bankrupt!".format(src)]}]
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Player {} parts Araboly game!".format(src)]}]
            if "newPlayers" in params and params["newPlayers"] == []:
                output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Stopping current Araboly game!"]}]
                return {"channel":channel, "context":context, "dice":dice, "output":output, "newField":newField, "newFieldBuyable":newFieldBuyable, "newFieldOwned":newFieldOwned, "newFieldPastGo":newFieldPastGo, "newPlayerCur":newPlayerCur, "src":src, **params}
        elif context.board[newField][0] == ArabolyGameField.TAX:
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Oh no! {} must pay ${}!".format(src, context.board[newField][1])]}]
        elif context.board[newField][0] == ArabolyGameField.PROPERTY  \
        or   context.board[newField][0] == ArabolyGameField.UTILITY:
            if not newFieldOwned:
                if not newFieldBuyable:
                    output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "{}: you don't have enough money to buy property {}!".format(src, context.board[newField][3])]}]
                    output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Entering auction mode!"]}]
                else:
                    output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "{}: buy property {}?".format(src, context.board[newField][3])]}]
            else:
                if not params["newFieldOwnedSelf"]:
                    for player in context.properties:
                        for playerProp in context.properties[player]:
                            if playerProp[-1] == newField:
                                propOwner = player
                    output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "{} pays ${} rent to {}!".format(src, params["newPropRent"], propOwner)]}]
        if newPlayerCur != context.playerCur:
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "{}: roll the dice!".format(context.players[newPlayerCur])]}]
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
        output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Player {} joins Araboly game!".format(src)]}]
        if (len(context.players) + len(params["newPlayers"])) == context.playersMax:
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Araboly game with {} players has started!".format(context.playersMax)]}]
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "{}: roll the dice!".format([*context.players, *params["newPlayers"]][context.playerCur])]}]
        return {"channel":channel, "context":context, "output":output, "src":src, **params}
    # }}}
    # {{{ dispatch_kick(self, channel, context, otherPlayer, output, **params): XXX
    def dispatch_kick(self, channel, context, otherPlayer, output, **params):
        output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Kicking {} from current Araboly game!".format(otherPlayer)]}]
        if len(context.players) <= 1:
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Stopping current Araboly game!"]}]
        return {"channel":channel, "context":context, "otherPlayer":otherPlayer, "output":output, **params}
    # }}}
    # {{{ dispatch_part(self, channel, context, output, src, **params): XXX
    def dispatch_part(self, channel, context, output, src, **params):
        output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Player {} parts Araboly game!".format(src)]}]
        if len(context.players) <= 1:
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Stopping current Araboly game!"]}]
        return {"channel":channel, "context":context, "output":output, "src":src, **params}
    # }}}
    # {{{ dispatch_pass(self, channel, context, output, src, **params): XXX
    def dispatch_pass(self, channel, context, output, src, **params):
        if context.state == ArabolyGameState.PROPERTY:
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "{} passes on {} for ${}!".format(src, context.board[context.fields[src]][3], context.board[context.fields[src]][1])]}]
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Entering auction mode!"]}]
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Current highest bid: $0"]}]
        elif context.state == ArabolyGameState.AUCTION:
            newHighestBid = params["newHighestBid"]; newHighestBidder = params["newHighestBidder"];
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "{} leaves auction for {}!".format(src, context.board[context.auctionProperty[-1]][3])]}]
            if newHighestBid != 0:
                if params["newAuctionEnd"]:
                    output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "{} buys {} for ${}!".format(newHighestBidder, context.board[context.auctionProperty[-1]][3], newHighestBid)]}]
                    output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "{}: roll the dice!".format(context.players[params["newPlayerCur"]])]}]
                else:
                    output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Current highest bid: ${}".format(newHighestBid)]}]
            else:
                if params["newAuctionEnd"]:
                    output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "The bank retains {}!".format(context.board[context.auctionProperty[-1]][3])]}]
                    output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "{}: roll the dice!".format(context.players[params["newPlayerCur"]])]}]
                else:
                    output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Current highest bid: $0"]}]
        return {"channel":channel, "context":context, "output":output, "src":src, **params}
    # }}}
    # {{{ dispatch_start(self, channel, context, output, players, src, **params): XXX
    def dispatch_start(self, channel, context, output, players, src, **params):
        output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Starting Araboly game with {} players!".format(players)]}]
        return {"channel":channel, "context":context, "output":output, "players":players, "src":src, **params}
    # }}}
    # {{{ dispatch_status(self, channel, context, output, src, **params): XXX
    def dispatch_status(self, channel, context, output, src, **params):
        if context.state == ArabolyGameState.GAME       \
        or context.state == ArabolyGameState.PROPERTY   \
        or context.state == ArabolyGameState.AUCTION:
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Araboly status for player {}:".format(src)]}]
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Field....: {}".format(context.board[context.fields[src]][3])]}]
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Wallet...: {}".format(context.wallets[src])]}]
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Properties owned:"]}]
            for prop in context.properties[src]:
                output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "${} -- {}, level {}, houses: {}".format(prop[1], prop[3], prop[4], str(prop[5][1:]))]}]
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Current turn: {}".format(context.players[context.playerCur])]}]
        return {"channel":channel, "context":context, "output":output, "src":src, **params}
    # }}}
    # {{{ dispatch_stop(self, channel output, **params): XXX
    def dispatch_stop(self, channel, output, **params):
        output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Stopping current Araboly game!"]}]
        return {"channel":channel, "output":output, **params}
    # }}}
    # {{{ dispatchError(self, output, **params): XXX
    def dispatchError(self, output, **params):
        if params["type"] == "command":
            if "channel" in params:
                output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[params["channel"], "general error!"]}]
                output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[params["channel"], "Monadic value: {}".format(str(params))]}]
                return {"output":output, **params}
        return {"output":output, **params}
    # }}}
    # {{{ dispatchException(self, e, exc_fname, exc_lineno, exc_stack, output, **params): XXX
    def dispatchException(self, e, exc_fname, exc_lineno, exc_stack, output, **params):
        if params["type"] == "command":
            if "channel" in params:
                output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[params["channel"], "Traceback (most recent call last):"]}]
                for stackLine in exc_stack:
                    output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[params["channel"], stackLine]}]
                output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[params["channel"], "{} exception in {}:{}: {}".format(e.__class__.__name__, exc_fname, exc_lineno, str(e))]}]
                output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[params["channel"], "Monadic value: {}".format(str(params))]}]
                return {"e":e, "output":output, **params}
        return {"e":e, "exc_fname":exc_fname, "exc_lineno":exc_lineno, "exc_stack":exc_stack, "output":output, **params}
    # }}}
    # {{{ __init__(self): initialisation method
    def __init__(self):
        with open("assets/ArabolyIrcBot.hlp", "r") as fileObject:
            self.helpLines = fileObject.readlines()
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120
