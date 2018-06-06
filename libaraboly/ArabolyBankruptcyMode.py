#!/usr/bin/env python3
#
# Araboly 2000 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from ArabolyFree import ArabolyFree
from ArabolyMonad import ArabolyDecorator
from ArabolyState import ArabolyGameState
from ArabolyTypeClass import ArabolyTypeClass

#@ArabolyDecorator(context={"state":ArabolyGameState.BANKRUPTCY})
class ArabolyBankruptcyMode(ArabolyTypeClass):
    """XXX"""

    # {{{ dispatch_lift(args, channel, context, output, src, srcFull, status): XXX
    @staticmethod
    def dispatch_lift(args, channel, context, output, src, srcFull, status):
        if  context.state != ArabolyGameState.BANKRUPTCY                    \
        and context.state != ArabolyGameState.GAME:
            status = False
        elif context.players["numMap"][context.players["curNum"]] != src    \
        or   len(args) != 1                                                 \
        or   int(args[0]) >= len(context.board):
            status = False
        else:
            fieldNum = int(args[0])
            field, srcPlayer = context.board[fieldNum], context.players["byName"][src]
            if not field["mortgaged"]                                       \
            or field["owner"] != src                                        \
            or (int(field["price"] / 2) * 1.10) >= srcPlayer["wallet"]:
                status = False
            else:
                mortgageAmount = int((field["price"] / 2) * 1.10)
                output = ArabolyFree._push_output(channel, context, output, "Awfom! {src} lifts the mortgage on {field[title]} and pays ${mortgageAmount} to the bank!".format(**locals()))
                output = ArabolyFree._push_output(channel, context, output, "Yay! {src} is now able to collect rent from and develop on {field[title]}!".format(**locals()))
                field["mortgaged"] = False
                srcPlayer["wallet"] -= mortgageAmount
        return args, channel, context, output, src, srcFull, status
    # }}}
    # {{{ dispatch_mortgage(args, channel, context, output, src, srcFull, status): XXX
    @staticmethod
    def dispatch_mortgage(args, channel, context, output, src, srcFull, status):
        if  context.state != ArabolyGameState.BANKRUPTCY                    \
        and context.state != ArabolyGameState.GAME:
            status = False
        elif context.players["numMap"][context.players["curNum"]] != src    \
        or   len(args) != 1                                                 \
        or   int(args[0]) >= len(context.board):
            status = False
        else:
            fieldNum = int(args[0])
            field, srcPlayer = context.board[fieldNum], context.players["byName"][src]
            if field["mortgaged"]                                           \
            or field["owner"] != src:
                status = False
            else:
                mortgageAmount = int(field["price"] / 2)
                output = ArabolyFree._push_output(channel, context, output, "Oops! {src} mortgages {field[title]} and receives ${mortgageAmount} from the bank!".format(**locals()))
                output = ArabolyFree._push_output(channel, context, output, "Oh no! {src} is no longer able to collect rent from or develop on {field[title]}!".format(**locals()))
                field["mortgaged"] = True
                srcPlayer["wallet"] += mortgageAmount
                if  context.state == ArabolyGameState.BANKRUPTCY            \
                and srcPlayer["wallet"] >= 200:
                    output = ArabolyFree._push_output(channel, context, output, "Awfom! {src} is no longer bankrupt at ${srcPlayer[wallet]}!".format(**locals()))
                    output = ArabolyFree._push_output(channel, context, output, "Leaving bankruptcy mode!")
                    context.state = ArabolyGameState.GAME
                    context, output = ArabolyFree._next_player(channel, context, output, src)
        return args, channel, context, output, src, srcFull, status
    # }}}

    # {{{ _enter(channel, context, output, src, srcPlayer): XXX
    @staticmethod
    def _enter(channel, context, output, src, srcPlayer):
        if srcPlayer["wallet"] <= 0:
            otherPlayers = [src]
            output = ArabolyFree._push_output(channel, context, output, "Oh no! {src} has gone bankrupt!".format(**locals()))
            srcCollateral = 0
            for srcPropNum in srcPlayer["properties"]:
                srcProp = context.board[srcPropNum]
                if srcProp["mortgaged"]:
                    continue
                else:
                    srcCollateral += int(srcProp["price"] / 2)
            if srcCollateral == 0:
                output = ArabolyFree._push_output(channel, context, output, "Player {src} parts Araboly game!".format(**locals()))
                context, output = ArabolyFree._remove_players(channel, context, output, otherPlayers)
                if len(context.players["numMap"]) <= 1:
                    output = ArabolyFree._status_final(channel, context, output)
            else:
                output = ArabolyFree._push_output(channel, context, output, "Entering bankruptcy mode!")
                output = ArabolyFree._push_output(channel, context, output, "{src}: mortgage properties until you've gained at least $200!".format(**locals()))
                context.state = ArabolyGameState.BANKRUPTCY
        return context, output
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=0
