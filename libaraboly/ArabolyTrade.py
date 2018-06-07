#!/usr/bin/env python3
#
# Araboly 2000 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from ArabolyGenerals import ArabolyGenerals
from ArabolyMonad import ArabolyDecorator
from ArabolyState import ArabolyGameField, ArabolyGameState, ArabolyStringType
from ArabolyTypeClass import ArabolyTypeClass

@ArabolyDecorator(context={"state":ArabolyGameState.GAME})
class ArabolyTrade(ArabolyTypeClass):
    """XXX"""

    # {{{ dispatch_accept(args, channel, cmd, context, output, src, status): XXX
    @staticmethod
    def dispatch_accept(args, channel, cmd, context, output, src, status):
        return ArabolyTrade._process_offer_reply(args, channel, cmd, context, output, src, status)
    # }}}
    # {{{ dispatch_buy(args, channel, cmd, context, output, src, status): XXX
    @staticmethod
    def dispatch_buy(args, channel, cmd, context, output, src, status):
        return ArabolyTrade._process_offer(args, channel, cmd, context, output, src, status)
    # }}}
    # {{{ dispatch_reject(args, channel, cmd, context, output, src, status): XXX
    @staticmethod
    def dispatch_reject(args, channel, cmd, context, output, src, status):
        return ArabolyTrade._process_offer_reply(args, channel, cmd, context, output, src, status)
    # }}}
    # {{{ dispatch_sell(args, channel, cmd, context, output, src, status): XXX
    @staticmethod
    def dispatch_sell(args, channel, cmd, context, output, src, status):
        return ArabolyTrade._process_offer(args, channel, cmd, context, output, src, status)
    # }}}

    # {{{ _leave(channel, context, output): XXX
    @staticmethod
    def _leave(channel, context, output):
        for tradeKey, tradeState in context.tradeState.items():
            if  not tradeKey.startswith(src + "\0") \
            and not tradeKey.endswith("\0" + src):
                continue
            else:
                if tradeState["counter"]:
                    typeString = tradeState["type"] + "counter-offer"
                else:
                    typeString = tradeState["type"] + " offer"
                output = ArabolyGenerals._push_output(channel, context, output, "Cancelling outstanding {} from {} to {} for {}!".format(typeString, tradeState["from"], tradeState["to"], tradeState["title"]))
                del context.tradeState[tradeKey]
        return channel, context, output
    # }}}
    # {{{ _process_offer(args, channel, cmd, context, output, src, status): XXX
    @staticmethod
    def _process_offer(args, channel, cmd, context, output, src, status):
        if len(args) != 3                                                       \
        or args[0] == src                                                       \
        or not args[0] in context.players["byName"]                             \
        or not args[1].isdigit()                                                \
        or int(args[1]) > len(context.board)                                    \
        or not args[2].isdigit()                                                \
        or int(args[2]) == 0:
            status = False
        else:
            offerType = cmd
            otherPlayer, field, price = args[0], context.board[int(args[1])], int(args[2])
            tradeKey, tradeKeyOld = src + "\0" + otherPlayer, otherPlayer + "\0" + src
            if  field["type"] != ArabolyGameField.PROPERTY                      \
            and field["type"] != ArabolyGameField.UTILITY:
                status = False
            elif not tradeKeyOld in context.tradeState:
                if context.players["numMap"][context.players["curNum"]] != src  \
                or tradeKey in context.tradeState:
                    status = False
                else:
                    counterOffer = False
            elif tradeKeyOld in context.tradeState:
                if  offerType == "buy"                                          \
                and context.tradeState[tradeKeyOld]["offerType"] != "sell":
                    status = False
                elif offerType == "sell"                                        \
                and  context.tradeState[tradeKeyOld]["offerType"] != "buy":
                    status = False
                else:
                    counterOffer = True
            if status:
                if offerType == "buy":
                    tradeFrom, tradeTo = otherPlayer, src
                elif offerType == "sell":
                    tradeFrom, tradeTo = src, otherPlayer
                if field["owner"] != tradeFrom                                  \
                or context.players["byName"][tradeTo]["wallet"] <= price:
                    status = False
                else:
                    tradeState = {"counter":counterOffer, "field":field["field"], "offerType":offerType, "otherPlayer":otherPlayer, "price":price, "src":src, "title":field["title"]}
                    offerString = "counter-offers" if counterOffer else "offers"
                    if offerType == "buy":
                        output = ArabolyGenerals._push_output(channel, context, output, "{otherPlayer}: {src} {offerString} to buy {title} from you at ${price}! Accept, counter-offer, or reject?".format(**{"offerString":offerString, **tradeState}))
                    elif offerType == "sell":
                        output = ArabolyGenerals._push_output(channel, context, output, "{otherPlayer}: {src} {offerString} to sell {title} to you at ${price}! Accept, counter-offer, or reject?".format(**{"offerString":offerString, **tradeState}))
                    if counterOffer:
                        del context.tradeState[tradeKeyOld]
                    context.tradeState[tradeKey] = tradeState
        return args, channel, cmd, context, output, src, status
    # }}}
    # {{{ _process_offer_reply(args, channel, cmd, context, output, src, status): XXX
    @staticmethod
    def _process_offer_reply(args, channel, cmd, context, output, src, status):
        if len(args) != 1   \
        or args[0] == src   \
        or not args[0] in context.players["byName"]:
            status = False
        else:
            otherPlayer, replyType, tradeKey = args[0], cmd, args[0] + "\0" + src
            if tradeKey not in context.tradeState:
                status = False
            else:
                tradeState = context.tradeState[tradeKey].copy()
                del context.tradeState[tradeKey]
                tradeState["replyType"] = replyType
                if tradeState["offerType"] == "buy":
                    tradePropFrom, tradePropTo = tradeState["otherPlayer"], tradeState["src"]
                    if tradeState["counter"]:
                        tradeState["offerType"] = "sell"
                elif tradeState["offerType"] == "sell":
                    tradePropFrom, tradePropTo = tradeState["src"], tradeState["otherPlayer"]
                    if tradeState["counter"]:
                        tradeState["offerType"] = "buy"
                tradeState["replyTypeString"] = "Yay" if replyType == "accept" else "Oh no"
                if tradeState["counter"]:
                    output = ArabolyGenerals._push_output(channel, context, output, "{src}: {replyTypeString}! {otherPlayer} {replyType}s your counter-offer to {offerType} {title} at ${price}!".format(**tradeState))
                else:
                    output = ArabolyGenerals._push_output(channel, context, output, "{src}: {replyTypeString}! {otherPlayer} {replyType}s your offer to {offerType} {title} at ${price}!".format(**tradeState))
                if replyType == "accept":
                    output = ArabolyGenerals._push_output(channel, context, output, "Awfom! {} buys {} for ${}!".format(tradePropTo, tradeState["title"], tradeState["price"]), 0.900)
                    context.players["byName"][tradePropFrom]["properties"].remove(tradeState["field"])
                    context.players["byName"][tradePropFrom]["wallet"] += tradeState["price"]
                    context, _, output = ArabolyGenerals._prop_recv(channel, context, context.board[tradeState["field"]], output, tradePropTo, tradeState["price"])
        return args, channel, cmd, context, output, src, status
    # }}}
    # {{{ _status(channel, context, output, statusPlayer): XXX
    def _status(channel, context, output, statusPlayer):
        tradesFrom, tradesTo = [], []
        for tradeKey, tradeState in context.tradeState.items():
            if tradeKey.startswith(statusPlayer + "\0"):
                if tradeState["counter"]:
                    tradeState = tradeState.copy()
                    if tradeState["offerType"] == "buy":
                        tradeState["direction"] = "to"
                        tradeState["offerType"] = "sell"
                    elif tradeState["offerType"] == "sell":
                        tradeState["direction"] = "from"
                        tradeState["offerType"] = "buy"
                    tradesFrom += ["{offerType} {title} {direction} {otherPlayer} for ${price} (counter)".format(**tradeState)]
                else:
                    tradesFrom += ["{offerType} {title} to {otherPlayer} for ${price}".format(**tradeState)]
            elif tradeKey.endswith("\0" + statusPlayer):
                if tradeState["counter"]:
                    tradeState = tradeState.copy()
                    if tradeState["offerType"] == "buy":
                        tradeState["direction"] = "to"
                        tradeState["offerType"] = "sell"
                    elif tradeState["offerType"] == "sell":
                        tradeState["direction"] = "from"
                        tradeState["offerType"] = "buy"
                    tradesTo += ["{offerType} {title} {direction} {src} for ${price} (counter)".format(**tradeState)]
                else:
                    tradesTo += ["{offerType} {title} from {src} for ${price}".format(**tradeState)]
        if len(tradesFrom):
            output = ArabolyGenerals._push_output(channel, context, output, "Pending offers from {}: {}".format(statusPlayer, ", ".join(tradesFrom)))
        if len(tradesTo):
            output = ArabolyGenerals._push_output(channel, context, output, "Pending offers to {}: {}".format(statusPlayer, ", ".join(tradesTo)))
        return output
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=0
