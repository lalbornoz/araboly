#!/usr/bin/env python3
#
# Araboly 2000 Advanced Server SP2 -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucio Andrés Illanes Albornoz <lucio@lucioillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from ArabolyAuctionMode import ArabolyAuctionMode
from ArabolyGenerals import ArabolyGenerals
from ArabolyMonad import ArabolyDecorator
from ArabolyState import ArabolyGameState
from ArabolyTypeClass import ArabolyTypeClass

@ArabolyDecorator(context={"state":ArabolyGameState.PROPERTY})
class ArabolyPropertyMode(ArabolyTypeClass):
    """XXX"""

    # {{{ dispatch_buy(args, channel, context, output, src, status): XXX
    @staticmethod
    def dispatch_buy(args, channel, context, output, src, status):
        if context.players["numMap"][context.players["curNum"]] != src  \
        or len(args):
            status = False
        else:
            srcPlayer = context.players["byName"][src]
            srcField = context.board[srcPlayer["field"]]
            output = ArabolyGenerals._push_output(channel, context, output, "{src} pays ${srcField[price]} to the bank!".format(**locals()))
            context, _, output = ArabolyGenerals._prop_recv(channel, context, srcField, output, src, srcField["price"])
            context.state = ArabolyGameState.GAME
            context, output = ArabolyGenerals._next_player(channel, context, output, src)
        return args, channel, context, output, src, status
    # }}}
    # {{{ dispatch_pass(args, channel, context, output, src, status): XXX
    @staticmethod
    def dispatch_pass(args, channel, context, output, src, status):
        if context.players["numMap"][context.players["curNum"]] != src  \
        or len(args):
            status = False
        else:
            srcField = context.board[context.players["byName"][src]["field"]]
            context, output = ArabolyAuctionMode._enter(channel, context, output, srcField)
        return args, channel, context, output, src, status
    # }}}

    # {{{ _enter(channel, context, output, src, srcField, srcPlayer): XXX
    @staticmethod
    def _enter(channel, context, output, src, srcField, srcPlayer):
        if srcField["price"] >= srcPlayer["wallet"]:
            output = ArabolyGenerals._push_output(channel, context, output, "{src}: you don't have enough money to buy property {srcField[title]}!".format(**locals()))
            context, output = ArabolyAuctionMode._enter(channel, context, output, srcField)
        else:
            output = ArabolyGenerals._push_output(channel, context, output, "{src}: buy property {srcField[title]}?".format(**locals()))
            context.state = ArabolyGameState.PROPERTY
        return context, output
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=0
