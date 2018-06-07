#!/usr/bin/env python3
#
# Araboly 2000 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from ArabolyGenerals import ArabolyGenerals
from ArabolyMonad import ArabolyDecorator
from ArabolyState import ArabolyGameState
from ArabolyTypeClass import ArabolyTypeClass

@ArabolyDecorator(context={"state":ArabolyGameState.AUCTION})
class ArabolyAuctionMode(ArabolyTypeClass):
    """XXX"""

    # {{{ dispatch_bid(args, channel, context, output, src, status): XXX
    @staticmethod
    def dispatch_bid(args, channel, context, output, src, status):
        if (len(args) != 1 or not args[0].isdigit()     \
        or  int(args[0]) == 0):
            status = False
        else:
            price, srcPlayer = int(args[0]), context.players["byName"][src]
            if srcPlayer["wallet"] <= price:
                status = False
            elif src in context.auctionState["bids"]    \
            and  context.auctionState["bids"][src] >= price:
                status = False
            else:
                for _, auctionBid in context.auctionState["bids"].items():
                    if auctionBid >= price:
                        status = False
        if status:
            flagAuctionEnd, highestBid, highestBidder, potentialBidders = ArabolyAuctionMode._process_auction(context, price, src)
            srcField = context.board[context.auctionState["field"]]
            output = ArabolyGenerals._push_output(channel, context, output, "{src} bids ${price} on {srcField[title]}!".format(**locals()))
            if flagAuctionEnd:
                output = ArabolyGenerals._push_output(channel, context, output, "Awfom! {highestBidder} wins the auction and buys {srcField[title]} for ${highestBid}!".format(**locals()))
                context, _, output = ArabolyGenerals._prop_recv(channel, context, context.board[context.auctionState["field"]], output, highestBidder, highestBid)
                context.auctionState["bids"].clear()
                context.auctionState["field"] = None
                context.state = ArabolyGameState.GAME
                context, output = ArabolyGenerals._next_player(channel, context, output, src)
            else:
                for player in [k for k,v in context.auctionState["bids"].items() if k != highestBidder and v > 0]:
                    output = ArabolyGenerals._push_output(channel, context, output, "{player}: you have been outbid by {highestBidder}! Place bid above ${price} or pass!".format(**locals()))
                    potentialBidders += [player]
                    del context.auctionState["bids"][player]
                output = ArabolyGenerals._push_output(channel, context, output, "Current highest bid: {highestBidder} at ${highestBid}".format(**locals()))
                output = ArabolyGenerals._push_output(channel, context, output, "Potential bidders remaining: {}".format(", ".join(potentialBidders)))
        return args, channel, context, output, src, status
    # }}}
    # {{{ dispatch_pass(args, channel, context, output, src, status): XXX
    @staticmethod
    def dispatch_pass(args, channel, context, output, src, status):
        if len(args):
            status = False
        else:
            if  src in context.auctionState["bids"] \
            and context.auctionState["bids"][src] == 0:
                status = False
        if status:
            flagAuctionEnd, highestBid, highestBidder, potentialBidders = ArabolyAuctionMode._process_auction(context, 0, src)
            srcField = context.board[context.auctionState["field"]]
            output = ArabolyGenerals._push_output(channel, context, output, "{src} leaves auction for {srcField[title]}!".format(**locals()))
            if flagAuctionEnd:
                if highestBid > 0:
                    output = ArabolyGenerals._push_output(channel, context, output, "Awfom! {highestBidder} wins the auction and buys {srcField[title]} for ${highestBid}!".format(**locals()))
                    context, _, output = ArabolyGenerals._prop_recv(channel, context, context.board[context.auctionState["field"]], output, highestBidder, highestBid)
                    context.auctionState["bids"].clear()
                    context.auctionState["field"] = None
                else:
                    output = ArabolyGenerals._push_output(channel, context, output, "The bank retains {srcField[title]}!".format(**locals()))
                context.state = ArabolyGameState.GAME
                context, output = ArabolyGenerals._next_player(channel, context, output, src)
            else:
                if highestBid != 0:
                    output = ArabolyGenerals._push_output(channel, context, output, "Current highest bid: {highestBidder} at ${highestBid}".format(**locals()))
                else:
                    output = ArabolyGenerals._push_output(channel, context, output, "No bids have been placed yet!")
                output = ArabolyGenerals._push_output(channel, context, output, "Potential bidders remaining: {}".format(", ".join(potentialBidders)))
        return args, channel, context, output, src, status
    # }}}

    # {{{ _enter(channel, context, output, srcField): XXX
    @staticmethod
    def _enter(channel, context, output, srcField):
        output = ArabolyGenerals._push_output(channel, context, output, "The bank auctions off {srcField[title]} (market price: ${srcField[price]})!".format(**locals()))
        output = ArabolyGenerals._push_output(channel, context, output, "Entering auction mode!")
        context.auctionState["bids"].clear()
        context.auctionState["field"] = srcField["field"]
        context.state = ArabolyGameState.AUCTION
        return context, output
    # }}}
    # {{{ _process_auction(context, price, src): XXX
    @staticmethod
    def _process_auction(context, price, src):
        context.auctionState["bids"][src] = price
        sortedBids = sorted(context.auctionState["bids"], key=context.auctionState["bids"].get)
        highestBid, highestBidder = context.auctionState["bids"][sortedBids[-1]], sortedBids[-1]
        numPositiveBids, potentialBidders = 0, list(set(context.players["byName"].keys()) - set(context.auctionState["bids"].keys()))
        for auctionBidder, auctionBid in context.auctionState["bids"].items():
            if auctionBid > 0:
                numPositiveBids += 1
        if  len(potentialBidders) == 0  \
        and numPositiveBids in [0,1]:
            flagAuctionEnd = True
        else:
            flagAuctionEnd = False
        return flagAuctionEnd, highestBid, highestBidder, potentialBidders
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=0
