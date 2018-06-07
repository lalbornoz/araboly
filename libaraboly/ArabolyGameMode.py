#!/usr/bin/env python3
#
# Araboly 2000 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from ArabolyBankruptcyMode import ArabolyBankruptcyMode
from ArabolyFree import ArabolyFree
from ArabolyMonad import ArabolyDecorator
from ArabolyPropertyMode import ArabolyPropertyMode
from ArabolyRtl import ArabolyAlignedReplace, ArabolyRandom
from ArabolyState import ArabolyGameField, ArabolyGameState, ArabolyOutputLevel, ArabolyStringType
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
                        output = ArabolyFree._push_output(channel, context, output, developString.format(owner=src, prop=field["title"], rands=rands))
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
            and ArabolyFree._authorised(channel, context, srcFull)      \
            or  context.clientParams["testing"]:
                dice = [int(args[0]), int(args[1])]
            else:
                status = False
        else:
            dice = [ArabolyRandom(max=6, min=1), ArabolyRandom(max=6, min=1)]
        if status:
            channel, context, output = ArabolyTrade._leave(channel, context, output)
            output = ArabolyFree._push_output(channel, context, output, "{src} rolls {dice[0]} and {dice[1]}!".format(**locals()))
            srcPlayer = context.players["byName"][src]
            srcField = context.board[(srcPlayer["field"] + dice[0] + dice[1]) % len(context.board)]
            srcFieldPastGo = srcField["field"] < srcPlayer["field"]
            srcPlayer["field"] = srcField["field"]

            output = ArabolyFree._board(channel, context, output, src)
            if srcFieldPastGo:
                srcPlayer["wallet"] += 200
                output = ArabolyFree._push_output(channel, context, output, "Yay! {src} passes past GO and collects $200!".format(**locals()))
            output = ArabolyFree._push_output(channel, context, output, "{src} lands on {srcField[title]}!".format(**locals()))

            if srcField["type"] == ArabolyGameField.PROPERTY            \
            or srcField["type"] == ArabolyGameField.UTILITY:
                if  srcField["owner"] == -1:
                    context, output = ArabolyPropertyMode._enter(channel, context, output, src, srcField, srcPlayer)
                elif srcField["owner"] != -1                            \
                and  srcField["owner"] != src:
                    if srcField["type"] == ArabolyGameField.PROPERTY:
                        srcPropRent = srcField["strings"][ArabolyStringType.RENT][srcField["level"]][0]
                        if  srcField["level"] == 0                      \
                        and srcField["ownerHasGroup"]:
                            srcPropRent *= 2
                    else:
                        srcPropRent = srcField["price"]
                    for rentString in srcField["strings"][ArabolyStringType.LAND][srcField["level"]]:
                        rands = [ArabolyRandom(limit=150-5, min=5) for x in range(10)]
                        output = ArabolyFree._push_output(channel, context, output, rentString.format(cost=srcPropRent, owner=srcField["owner"], prop=srcField["title"], rands=rands, who=src))
                    srcPlayer["wallet"] -= srcPropRent
            elif srcField["type"] == ArabolyGameField.TAX:
                output = ArabolyFree._push_output(channel, context, output, "Oh no! {src} must pay ${srcField[price]}!".format(**locals()))
                srcPlayer["wallet"] -= srcField["price"]

            if context.state == ArabolyGameState.GAME:
                if srcPlayer["wallet"] <= 0:
                    context, output = ArabolyBankruptcyMode._enter(channel, context, output, src, srcPlayer)
                if  context.state == ArabolyGameState.GAME              \
                and len(context.players["numMap"]) > 1:
                    context, output = ArabolyFree._next_player(channel, context, output, src)
        return args, channel, context, output, src, srcFull, status
    # }}}
    # {{{ dispatch_status(args, channel, context, output, src, status): XXX
    def dispatch_status(args, channel, context, output, src, status):
        if len(args) == 0:
            statusPlayer = src
        elif len(args) == 1:
            if not args[0] in context.players["byName"]:
                status = False
            else:
                statusPlayer = args[0]
        if status:
            playerField = context.board[context.players["byName"][statusPlayer]["field"]]
            playerProps = context.players["byName"][statusPlayer]["properties"]
            playerWallet = context.players["byName"][statusPlayer]["wallet"]
            output = ArabolyFree._push_output(channel, context, output, "Araboly status for player {statusPlayer}:".format(**locals()), outputLevel=ArabolyOutputLevel.LEVEL_GRAPHICS)
            output = ArabolyFree._push_output(channel, context, output, "Field....: {playerField[title]}".format(**locals()), outputLevel=ArabolyOutputLevel.LEVEL_GRAPHICS)
            output = ArabolyFree._push_output(channel, context, output, "Wallet...: ${playerWallet}".format(**locals()), outputLevel=ArabolyOutputLevel.LEVEL_GRAPHICS)
            if len(playerProps):
                output = ArabolyFree._push_output(channel, context, output, "Properties owned:", outputLevel=ArabolyOutputLevel.LEVEL_GRAPHICS)
                for playerPropNum in playerProps:
                    playerProp = context.board[playerPropNum]
                    mortgagedString = " (\u001fMORTGAGED\u001f)" if playerProp["mortgaged"] else ""
                    developmentsList = []
                    for levelNum in range(playerProp["level"] + 1):
                        developmentsList += playerProp["strings"][ArabolyStringType.NAME][levelNum]
                    developmentsString = " developments: {}".format(", ".join(developmentsList))
                    output = ArabolyFree._push_output(channel, context, output, "\u0003{:02d}${}{} (#{}) -- {},{}".format(playerProp["colourMiRC"], playerProp["price"], mortgagedString, playerProp["field"], playerProp["title"], developmentsString), outputLevel=ArabolyOutputLevel.LEVEL_GRAPHICS)
            output = ArabolyTrade._status(channel, context, output, statusPlayer)
            output = ArabolyFree._push_output(channel, context, output, "Current turn: {}".format(context.players["numMap"][context.players["curNum"]]), outputLevel=ArabolyOutputLevel.LEVEL_GRAPHICS)
        return args, channel, context, output, src, status
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=0
