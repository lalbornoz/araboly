#!/usr/bin/env python3
#
# Araboly 2000 Advanced Server SP4 -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from ArabolyBankruptcyMode import ArabolyBankruptcyMode
from ArabolyGenerals import ArabolyGenerals
from ArabolyFields import ArabolyFields
from ArabolyMonad import ArabolyDecorator
from ArabolyRtl import ArabolyRandom
from ArabolyState import ArabolyGameField, ArabolyGameState, ArabolyStringType
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
            if  field["type"] != ArabolyGameField.CHRONO                \
            and field["type"] != ArabolyGameField.PROPERTY              \
            and field["type"] != ArabolyGameField.UTILITY:
                status = False
            else:
                if context.players["difficulty"] == "hard":
                    devCost = field["devCost"] * 2
                else:
                    devCost = field["devCost"]
            if devCost >= srcPlayer["wallet"]                           \
            or field["mortgaged"]                                       \
            or field["owner"] != src:
                status = False
            elif field["type"] == ArabolyGameField.CHRONO:
                if not (field["level"] == 0 and newLevel == 1):
                    status = False
                else:
                    field["level"] = newLevel
                    for developString in field["strings"][ArabolyStringType.DEVELOP][newLevel]:
                        rands = [ArabolyRandom(limit=150-5, min=5) for x in range(10)]
                        output = ArabolyGenerals._push_output(channel, context, output, developString.format(owner=src, prop=field["title"], rands=rands))
                    srcPlayer["wallet"] -= devCost
            else:
                if  not field["ownerHasGroup"]                          \
                and context.players["difficulty"] != "hard":
                    status = False
                elif field["level"] == newLevel:
                    status = False
                else:
                    for otherFieldNum in field["groupFields"]:
                        otherField = context.board[otherFieldNum]
                        if  otherField["level"] != newLevel             \
                        and otherField["level"] != (newLevel - 1):
                            status = False; break;
                    if status:
                        field["level"] = newLevel
                        for developString in field["strings"][ArabolyStringType.DEVELOP][newLevel]:
                            rands = [ArabolyRandom(limit=150-5, min=5) for x in range(10)]
                            output = ArabolyGenerals._push_output(channel, context, output, developString.format(owner=src, prop=field["title"], rands=rands))
                        srcPlayer["wallet"] -= devCost
        return args, channel, context, output, src, status
    # }}}
    # {{{ dispatch_dice(args, channel, context, output, src, srcFull, status): XXX
    @staticmethod
    def dispatch_dice(args, channel, context, output, src, srcFull, status):
        if context.players["numMap"][context.players["curNum"]] != src:
            status = False
        elif len(args):
            if  len(args) >= 2                                          \
            and ArabolyGenerals._authorised(channel, context, srcFull)  \
            or  context.clientParams["testing"]:
                dice = [int(args[0]), int(args[1])]
            else:
                status = False
        else:
            dice = [ArabolyRandom(max=6, min=1), ArabolyRandom(max=6, min=1)]
        if status:
            if context.clientParams["recording"]:
                context.clientParams["recordingXxxLastArgs"] = dice
            channel, context, src, output = ArabolyTrade._leave(channel, context, src, output)
            output = ArabolyGenerals._push_output(channel, context, output, "{src} rolls {dice[0]} and {dice[1]}!".format(**locals()))
            srcPlayer = context.players["byName"][src]
            srcField = context.board[srcPlayer["field"]]
            if "loonyBinTurns" in srcPlayer:
                context, output, srcPlayer = ArabolyGameMode._dice_loony_bin(channel, context, dice, output, src, srcPlayer)
            else:
                srcField = context.board[(srcPlayer["field"] + dice[0] + dice[1]) % len(context.board)]
                srcFieldPastGo = srcField["field"] < srcPlayer["field"]
                srcPlayer["field"] = srcField["field"]
                output = ArabolyGenerals._board(channel, context, output, src)
                if dice[0] == dice[1]:
                    context, output, srcField, srcPlayer, status = ArabolyGameMode._dice_doubles(args, channel, context, dice, output, src, srcField, srcFieldPastGo, srcFull, srcPlayer, status)
                else:
                    if "doubles" in srcPlayer:
                        del srcPlayer["doubles"]
                    context, output, srcField, srcPlayer, status = ArabolyFields._land_field(args[2:], channel, context, output, src, srcField, srcFieldPastGo, srcFull, srcPlayer, status)
            if context.state == ArabolyGameState.GAME:
                if srcPlayer["wallet"] <= 0:
                    context, output = ArabolyBankruptcyMode._enter(channel, context, output, src, srcPlayer)
                if  context.state == ArabolyGameState.GAME              \
                and len([n for n in context.players["numMap"] if n != None]) > 1:
                    context, output = ArabolyGenerals._next_player(channel, context, output, src)
        return args, channel, context, output, src, srcFull, status
    # }}}

    # {{{ _dice_doubles(args, channel, context, dice, output, src, srcField, srcFieldPastGo, srcFull, srcPlayer, status): XXX
    @staticmethod
    def _dice_doubles(args, channel, context, dice, output, src, srcField, srcFieldPastGo, srcFull, srcPlayer, status):
        if not "doubles" in srcPlayer:
            srcPlayer["doubles"] = 1
        else:
            srcPlayer["doubles"] += 1
        if srcPlayer["doubles"] == 2:
            del srcPlayer["doubles"]
            srcField, srcPlayer["field"] = context.board[30], 30
            output = ArabolyGenerals._push_output(channel, context, output, "Oh dear! {src} has rolled doubles two times in a row and is sent to the loony bin!".format(**locals()))
        else:
            output = ArabolyGenerals._push_output(channel, context, output, "Oops! {src} has rolled doubles!".format(**locals()))
        context, output, srcField, srcPlayer, status = ArabolyFields._land_field(args[2:], channel, context, output, src, srcField, srcFieldPastGo, srcFull, srcPlayer, status)
        return context, output, srcField, srcPlayer, status
    # }}}
    # {{{ _dice_loony_bin(channel, context, dice, output, src, srcPlayer): XXX
    @staticmethod
    def _dice_loony_bin(channel, context, dice, output, src, srcPlayer):
        srcPlayer["loonyBinTurns"] += 1
        if dice[0] == dice[1]:
            output = ArabolyGenerals._push_output(channel, context, output, "Awfom! {src} has rolled doubles and is released from the loony bin!".format(**locals()))
            del srcPlayer["loonyBinTurns"]
        elif srcPlayer["loonyBinTurns"] == 3:
            output = ArabolyGenerals._push_output(channel, context, output, "Yay! {src} is released from the loony bin after {srcPlayer[loonyBinTurns]} turns!".format(**locals()))
            output = ArabolyGenerals._push_output(channel, context, output, "Oops! {src} has not rolled doubles and must pay $100 to the loony bin!".format(**locals()))
            srcPlayer["wallet"] -= 100
            del srcPlayer["loonyBinTurns"]
        else:
            output = ArabolyGenerals._push_output(channel, context, output, "Oops! {src} has not rolled doubles and must stay in the loony bin!".format(**locals()))
        return context, output, srcPlayer
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=0
