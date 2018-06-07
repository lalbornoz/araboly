#!/usr/bin/env python3
#
# Araboly 2000 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

import ArabolyAttractMode
from ArabolyMonad import ArabolyDecorator
from ArabolyRtl import ArabolyAlignedReplace, ArabolyRandom
from ArabolyTypeClass import ArabolyTypeClass
from ArabolyState import ArabolyGameField, ArabolyGameState, ArabolyOutputLevel, ArabolyStringType
from fnmatch import fnmatch
import time

@ArabolyDecorator()
class ArabolyFree(ArabolyTypeClass):
    """XXX"""

    # {{{ dispatch_board(args, channel, context, output, src, status): XXX
    @staticmethod
    def dispatch_board(args, channel, context, output, src, status):
        if  context.state != ArabolyGameState.AUCTION   \
        and context.state != ArabolyGameState.GAME      \
        and context.state != ArabolyGameState.PROPERTY:
            status = False
        elif len(args)                                  \
        or   src not in context.players["byName"]:
            status = False
        else:
            output = ArabolyFree._board(channel, context, output, src)
        return args, channel, context, output, src, status
    # }}}
    # {{{ dispatch_help(channel, context): XXX
    @staticmethod
    def dispatch_help(channel, context, output):
        for helpLine in context.graphics["help"]:
            output = ArabolyFree._push_output(channel, context, output, helpLine, outputLevel=ArabolyOutputLevel.LEVEL_GRAPHICS)
        return channel, context, output
    # }}}
    # {{{ dispatch_kick(args, channel, context, output, srcFull, status): XXX
    @staticmethod
    def dispatch_kick(args, channel, context, output, srcFull, status):
        if context.state == ArabolyGameState.GAME   \
        or context.state == ArabolyGameState.SETUP:
            if len(args) != 1 or len(args[0]) < 1   \
            or args[0] not in context.players["byName"]:
                status = False
            elif ArabolyFree._authorised(channel, context, srcFull):
                otherPlayers = [args[0]]
                output = ArabolyFree._push_output(channel, context, output, "Kicking {args[0]} from current Araboly game!".format(**locals()))
                context, output = ArabolyFree._remove_players(channel, context, output, otherPlayers)
        else:
            status = False
        return args, channel, context, output, srcFull, status
    # }}}
    # {{{ dispatch_melp(channel, context, output): XXX
    @staticmethod
    def dispatch_melp(channel, context, output):
        for explosionLine in context.graphics["explosion"]:
            output = ArabolyFree._push_output(channel, context, output, explosionLine, outputLevel=ArabolyOutputLevel.LEVEL_GRAPHICS)
        output = ArabolyFree._push_output(channel, context, output, "\u0001ACTION explodes.\u0001", outputLevel=ArabolyOutputLevel.LEVEL_GRAPHICS)
        return channel, context, output
    # }}}
    # {{{ dispatch_part(args, channel, context, output, src, status): XXX
    @staticmethod
    def dispatch_part(args, channel, context, output, src, status):
        if context.state == ArabolyGameState.GAME   \
        or context.state == ArabolyGameState.SETUP:
            if len(args) > 0    \
            or src not in context.players["byName"]:
                status = False
            else:
                otherPlayers = [src]
                output = ArabolyFree._push_output(channel, context, output, "Player {src} parts Araboly game!".format(**locals()))
                context, output = ArabolyFree._remove_players(channel, context, output, otherPlayers)
        else:
            status = False
        return args, channel, context, output, src, status
    # }}}
    # {{{ dispatch_stop(args, channel, context, output, src, srcFull, status): XXX
    @staticmethod
    def dispatch_stop(args, channel, context, output, src, srcFull, status):
        if context.state == ArabolyGameState.GAME   \
        or context.state == ArabolyGameState.SETUP:
            if len(args) > 0:
                status = False
            elif ArabolyFree._authorised(channel, context, srcFull):
                otherPlayers = list(context.players["byName"].keys())
                context, output = ArabolyFree._remove_players(channel, context, output, otherPlayers)
        else:
            status = False
        return args, channel, context, output, src, srcFull, status
    # }}}

    # {{{ _authorised(channel, context, srcFull): XXX
    @staticmethod
    def _authorised(channel, context, srcFull):
        if context.clientParams["hostname"] == None:
            hostname = "127.0.0.1"
        else:
            hostname = context.clientParams["hostname"]
        for uafItem in context.clientParams["uaf"]:
            if  fnmatch(hostname, uafItem["hostnameMask"]) \
            and fnmatch(channel, uafItem["channelMask"])   \
            and fnmatch(srcFull, uafItem["clientMask"]):
                return True
        return False
    # }}}
    # {{{ _board(channel, context, output, src): XXX
    @staticmethod
    def _board(channel, context, output, src):
        field = context.players["byName"][src]["field"]
        for fieldMin, fieldMax, fieldBoardLines in context.graphics["fields"]:
            if field >= fieldMin and field <= fieldMax:
                for boardLine in fieldBoardLines:
                    boardPatterns = ["< CURRENT FIELD TITLE1 >", "< CURRENT FIELD TITLE2 >"]
                    if  boardLine.find(boardPatterns[0])    \
                    and boardLine.find(boardPatterns[1]):
                        boardLine = ArabolyAlignedReplace(boardLine, boardPatterns, context.board[field]["title"])
                    boardPatterns = ["< PLAYER NAME HERE >"]
                    if  boardLine.find(boardPatterns[0]):
                        boardLine = ArabolyAlignedReplace(boardLine, boardPatterns, src)
                    output = ArabolyFree._push_output(channel, context, output, boardLine, outputLevel=ArabolyOutputLevel.LEVEL_GRAPHICS)
        return output
    # }}}
    # {{{ _next_player(channel, context, output, src): XXX
    @staticmethod
    def _next_player(channel, context, output, src):
        context.players["curNum"] = (context.players["curNum"] + 1) % len(context.players["numMap"])
        output = ArabolyFree._push_output(channel, context, output, "{}: roll the dice!".format(context.players["numMap"][context.players["curNum"]]))
        return context, output
    # }}}
    # {{{ _prop_recv(channel, context, field, output, newOwner=None, price=None): XXX
    def _prop_recv(channel, context, field, output, newOwner=None, price=None):
        for buyString in field["strings"][ArabolyStringType.DEVELOP][0]:
            rands = [ArabolyRandom(limit=150-5, min=5) for x in range(10)]
            output = ArabolyFree._push_output(channel, context, output, buyString.format(owner=newOwner, prop=field["title"], rands=rands))
        field["owner"] = newOwner
        context.players["byName"][newOwner]["properties"] += [field["field"]]
        context.players["byName"][newOwner]["wallet"] -= price
        if field["type"] == ArabolyGameField.PROPERTY:
            hasGroupFields = True
            for otherFieldNum in field["groupFields"]:
                otherField = context.board[otherFieldNum]
                if otherField["owner"] != newOwner:
                    hasGroupFields = False; break;
            if hasGroupFields:
                for otherFieldNum in field["groupFields"]:
                    otherField = context.board[otherFieldNum]
                    otherField["ownerHasGroup"] = True
        return context, field, output
    # }}}
    # {{{ _push_output(channel, context, output, msg, outputLevel=None): XXX
    @staticmethod
    def _push_output(channel, context, output, msg, outputLevel=None):
        output += [{"eventType":"message", "cmd":"PRIVMSG", "args":[channel, msg]}]
        if outputLevel != None:
            output[-1]["outputLevel"] = outputLevel
        return output
    # }}}
    # {{{ _remove_players(channel, context, output, otherPlayers=None): XXX
    @staticmethod
    def _remove_players(channel, context, output, otherPlayers=None):
        if (len(context.players["numMap"]) - len(otherPlayers)) <= 1:
            output = ArabolyFree._status_final(channel, context, output)
            output = ArabolyFree._push_output(channel, context, output, "Stopping current Araboly game!")
            otherPlayers = list(context.players["byName"].keys())
            output = ArabolyAttractMode.ArabolyAttractMode._enter(channel, context, output)
        for otherPlayerName in otherPlayers:
            otherPlayer = context.players["byName"][otherPlayerName]
            for propField in otherPlayer["properties"]:
                otherProp = context.board[propField]
                otherProp["mortgaged"] = False
                otherProp["owner"] = -1
                otherProp["ownerHasGroup"] = False
            del context.players["byName"][otherPlayer["name"]]
            context.players["numMap"].remove(otherPlayer["name"])
            if context.players["curNum"] > 0:
                context.players["curNum"] -= 1
        return context, output
    # }}}
    # {{{ _status_final(channel, context, output): XXX
    @staticmethod
    def _status_final(channel, context, output):
        if len(context.players["byName"]) > 1:
            output = ArabolyFree._push_output(channel, context, output, "List of players:", outputLevel=ArabolyOutputLevel.LEVEL_GRAPHICS)
            playerWinner, sortedNum = None, 0
            for playerItem in sorted(context.players["byName"].items(), key=lambda i: i[1]["wallet"], reverse=True):
                playerItem, sortedNum = playerItem[1], sortedNum + 1
                if sortedNum == 1:
                    playerWinner = playerItem
                if len(playerItem["properties"]):
                    output = ArabolyFree._push_output(channel, context, output, "{sortedNum: 2d}: {playerItem[name]} at ${playerItem[wallet]}, properties owned:".format(**locals()), outputLevel=ArabolyOutputLevel.LEVEL_GRAPHICS)
                    for playerPropNum in playerItem["properties"]:
                        playerProp = context.board[playerPropNum]
                        mortgagedString = " (\u001fMORTGAGED\u001f)" if playerProp["mortgaged"] else ""
                        developmentsList = []
                        for levelNum in range(playerProp["level"] + 1):
                            developmentsList += playerProp["strings"][ArabolyStringType.NAME][levelNum]
                        developmentsString = " developments: {}".format(", ".join(developmentsList))
                        output = ArabolyFree._push_output(channel, context, output, "    \u0003{:02d}${}{} (#{}) -- {},{}".format(playerProp["colourMiRC"], playerProp["price"], mortgagedString, playerProp["field"], playerProp["title"], developmentsString), outputLevel=ArabolyOutputLevel.LEVEL_GRAPHICS)
                else:
                    output = ArabolyFree._push_output(channel, context, output, "{sortedNum: 2d}: {playerItem[name]} at ${playerItem[wallet]}, no properties owned!".format(**locals()), outputLevel=ArabolyOutputLevel.LEVEL_GRAPHICS)
            output = ArabolyFree._push_output(channel, context, output, "Awfom! {playerWinner[name]} has won the game at ${playerWinner[wallet]}!".format(**locals()), outputLevel=ArabolyOutputLevel.LEVEL_GRAPHICS)
        else:
            output = ArabolyFree._push_output(channel, context, output, "Oops! Nobody has won the game!", outputLevel=ArabolyOutputLevel.LEVEL_GRAPHICS)
        return output
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=0
