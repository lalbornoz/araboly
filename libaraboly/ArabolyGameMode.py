#!/usr/bin/env python3
#
# Araboly 2000 Advanced Server SP2 -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucio Andrés Illanes Albornoz <lucio@lucioillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from ArabolyBankruptcyMode import ArabolyBankruptcyMode
from ArabolyGenerals import ArabolyGenerals
from ArabolyFields import ArabolyFields
from ArabolyMonad import ArabolyDecorator
from ArabolyRtl import ArabolyRandom
from ArabolyState import ArabolyGameState, ArabolyStringType
from ArabolyTrade import ArabolyTrade
from ArabolyTypeClass import ArabolyTypeClass

@ArabolyDecorator(context={"state":ArabolyGameState.GAME})
class ArabolyGameMode(ArabolyTypeClass):
    """XXX"""

    # {{{ dispatch_develop(args, channel, context, output, src, status): XXX
    @staticmethod
    def dispatch_develop(args, channel, context, output, src, status):
        if context.players["numMap"][context.players["curNum"]] != src  \
        or len(args) != 2                                               \
        or not args[0].isdigit() or not args[1].isdigit()               \
        or int(args[0]) >= len(context.board)                           \
        or int(args[1]) == 0 or int(args[1]) > 3:
            status = False
        else:
            fieldNum, newLevel = int(args[0]), int(args[1])
            field, srcPlayer = context.board[fieldNum], context.players["byName"][src]
            if field["devCost"] >= srcPlayer["wallet"]                  \
            or field["mortgaged"]                                       \
            or field["owner"] != src                                    \
            or not field["ownerHasGroup"]:
                status = False
            else:
                for otherFieldNum in field["groupFields"]:
                    otherField = context.board[otherFieldNum]
                    if  otherField["level"] != newLevel                 \
                    and otherField["level"] != (newLevel - 1):
                        status = False; break;
                if status:
                    field["level"] = newLevel
                    for developString in field["strings"][ArabolyStringType.DEVELOP][newLevel]:
                        rands = [ArabolyRandom(limit=150-5, min=5) for x in range(10)]
                        output = ArabolyGenerals._push_output(channel, context, output, developString.format(owner=src, prop=field["title"], rands=rands))
                    srcPlayer["wallet"] -= field["devCost"]
        return args, channel, context, output, src, status
    # }}}
    # {{{ dispatch_dice(args, channel, context, output, src, srcFull, status): XXX
    @staticmethod
    def dispatch_dice(args, channel, context, output, src, srcFull, status):
        if context.players["numMap"][context.players["curNum"]] != src:
            status = False
        elif len(args):
            if  len(args) == 2                                          \
            and ArabolyGenerals._authorised(channel, context, srcFull)  \
            or  context.clientParams["testing"]:
                dice = [int(args[0]), int(args[1])]
            else:
                status = False
        else:
            dice = [ArabolyRandom(max=6, min=1), ArabolyRandom(max=6, min=1)]
        if status:
            channel, context, src, output = ArabolyTrade._leave(channel, context, src, output)
            output = ArabolyGenerals._push_output(channel, context, output, "{src} rolls {dice[0]} and {dice[1]}!".format(**locals()))
            srcPlayer = context.players["byName"][src]
            srcField = context.board[(srcPlayer["field"] + dice[0] + dice[1]) % len(context.board)]
            srcFieldPastGo = srcField["field"] < srcPlayer["field"]
            srcPlayer["field"] = srcField["field"]
            output = ArabolyGenerals._board(channel, context, output, src)
            context, output, srcField, srcPlayer = ArabolyFields._land_field(channel, context, output, src, srcField, srcFieldPastGo, srcPlayer)
            if context.state == ArabolyGameState.GAME:
                if srcPlayer["wallet"] <= 0:
                    context, output = ArabolyBankruptcyMode._enter(channel, context, output, src, srcPlayer)
                if  context.state == ArabolyGameState.GAME              \
                and len(context.players["numMap"]) > 1:
                    context, output = ArabolyGenerals._next_player(channel, context, output, src)
        return args, channel, context, output, src, srcFull, status
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=0
