#!/usr/bin/env python3
#
# Araboly 2000 Advanced Server SP3 -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

import ArabolyAttractMode
from ArabolyMonad import ArabolyDecorator
from ArabolyRtl import ArabolyAlignedReplace, ArabolyRandom
from ArabolyTypeClass import ArabolyTypeClass
from ArabolyState import ArabolyGameField, ArabolyOutputLevel, ArabolyStringType
from fnmatch import fnmatch
import re

@ArabolyDecorator()
class ArabolyGenerals(ArabolyTypeClass):
    """XXX"""

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
                fieldBoardLines = fieldBoardLines.copy()
                for lineNum in range(len(fieldBoardLines)):
                    boardLine = fieldBoardLines[lineNum]
                    boardPatterns = ["< CURRENT FIELD TITLE1 >", "< CURRENT FIELD TITLE2 >"]
                    if  boardLine.find(boardPatterns[0])    \
                    and boardLine.find(boardPatterns[1]):
                        boardLine = ArabolyAlignedReplace(boardLine, boardPatterns, context.board[field]["title"])
                    boardPatterns = ["< PLAYER NAME HERE >"]
                    if  boardLine.find(boardPatterns[0]):
                        boardLine = ArabolyAlignedReplace(boardLine, boardPatterns, src)
                    fieldBoardLines[lineNum] = boardLine
                if "hie" in context.players["byName"][src]:
                    fieldBoardLines = ArabolyGenerals._board_hie(fieldBoardLines)
                for boardLine in fieldBoardLines:
                    output = ArabolyGenerals._push_output(channel, context, output, boardLine, outputLevel=ArabolyOutputLevel.LEVEL_GRAPHICS)
                if "hie" in context.players["byName"][src]:
                    output = ArabolyGenerals._push_output(channel, context, output, "Oh shit! {src} is hie as fuck!".format(**locals()), delay=1.5)
        return output
    # }}}
    # {{{ _board_hie(fieldBoardLines): XXX
    @staticmethod
    def _board_hie(fieldBoardLines):
        hieDecision = ArabolyRandom(max=3, min=1)
        if hieDecision == 1:
            fieldBoardLines.reverse()
        elif hieDecision == 2:
            for lineNum in range(len(fieldBoardLines)):
                newLine = fieldBoardLines[lineNum]
                for match in re.finditer("[a-zA-Z]{2,}", newLine):
                    newString = "G" + ("R" * (len(match.group(0)) - 1))
                    newLine = newLine[:match.start()] + newString + newLine[match.end():]
                fieldBoardLines[lineNum] = newLine
        elif hieDecision == 3:
            for lineNum in range(len(fieldBoardLines)):
                newLine = fieldBoardLines[lineNum]
                for match in re.finditer("\u0003(1[0-5]|0?[0-9]),(1[0-5]|0?[0-9])", newLine):
                    if len(match.group(1)) == 1:
                        newColours = "\u0003" + str(ArabolyRandom(max=9, min=0))
                    elif len(match.group(1)) == 2:
                        newColours = "\u0003{:02d}".format(ArabolyRandom(max=15, min=0))
                    if len(match.group(2)) == 1:
                        newColours += "," + str(ArabolyRandom(max=9, min=0))
                    elif len(match.group(2)) == 2:
                        newColours += ",{:02d}".format(ArabolyRandom(max=15, min=0))
                    newLine = newLine[:match.start()] + newColours + newLine[match.end():]
                fieldBoardLines[lineNum] = newLine
        return fieldBoardLines
    # }}}
    # {{{ _next_player(channel, context, output, src): XXX
    @staticmethod
    def _next_player(channel, context, output, src):
        context.players["curNum"] = (context.players["curNum"] + 1) % len(context.players["numMap"])
        output = ArabolyGenerals._push_output(channel, context, output, "{}: roll the dice!".format(context.players["numMap"][context.players["curNum"]]))
        return context, output
    # }}}
    # {{{ _prop_recv(channel, context, field, output, newOwner=None, price=None): XXX
    def _prop_recv(channel, context, field, output, newOwner=None, price=None):
        for buyString in field["strings"][ArabolyStringType.DEVELOP][0]:
            rands = [ArabolyRandom(limit=150-5, min=5) for x in range(10)]
            output = ArabolyGenerals._push_output(channel, context, output, buyString.format(owner=newOwner, prop=field["title"], rands=rands))
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
    # {{{ _push_output(channel, context, output, msg, outputLevel=None, delay=None): XXX
    @staticmethod
    def _push_output(channel, context, output, msg, outputLevel=None, delay=None):
        output += [{"eventType":"message", "cmd":"PRIVMSG", "args":[channel, msg]}]
        if outputLevel != None:
            output[-1]["outputLevel"] = outputLevel
        if delay != None:
            output[-1]["delay"] = delay
        return output
    # }}}
    # {{{ _remove_players(channel, context, output, otherPlayers=None): XXX
    @staticmethod
    def _remove_players(channel, context, output, otherPlayers=None):
        if (len(context.players["numMap"]) - len(otherPlayers)) <= 1:
            output = ArabolyGenerals._status_final(channel, context, output)
            output = ArabolyGenerals._push_output(channel, context, output, "Stopping current Araboly game!")
            otherPlayers = list(context.players["byName"].keys())
            output = ArabolyAttractMode.ArabolyAttractMode._enter(channel, context, output)
            if context.clientParams["recording"]:
                context.clientParams["recordingXxxGameEnded"] = True
        for otherPlayerName in otherPlayers:
            otherPlayer = context.players["byName"][otherPlayerName]
            for propField in otherPlayer["properties"]:
                otherProp = context.board[propField]
                otherProp["level"] = 0
                otherProp["mortgaged"] = False
                otherProp["owner"] = -1
                if otherProp["type"] == ArabolyGameField.PROPERTY:
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
            finalPlayers = {}
            for playerName, player in context.players["byName"].items():
                finalPlayers[playerName] = {"name":player["name"], "netWorth":player["wallet"], "properties":player["properties"], "wallet":player["wallet"]}
                for playerPropNum in player["properties"]:
                    playerProp = context.board[playerPropNum]
                    if playerProp["mortgaged"]:
                        finalPlayers[playerName]["netWorth"] += int(playerProp["price"] / 2)
                    else:
                        finalPlayers[playerName]["netWorth"] += playerProp["price"]
            output = ArabolyGenerals._push_output(channel, context, output, "List of players:")
            playerWinner, sortedNum = None, 0
            for player in sorted(finalPlayers.items(), key=lambda i: i[1]["netWorth"], reverse=True):
                playerName, player, sortedNum = player[0], player[1], sortedNum + 1
                if sortedNum == 1:
                    playerWinner = player
                if len(player["properties"]):
                    output = ArabolyGenerals._push_output(channel, context, output, "{sortedNum: 2d}: {player[name]} at ${player[netWorth]} (wallet: ${player[wallet]},) properties owned:".format(**locals()), outputLevel=ArabolyOutputLevel.LEVEL_NODELAY)
                    for playerPropNum in player["properties"]:
                        playerProp = context.board[playerPropNum]
                        mortgagedString = " (\u001fMORTGAGED\u001f)" if playerProp["mortgaged"] else ""
                        developmentsList = []
                        for levelNum in range(playerProp["level"] + 1):
                            developmentsList += playerProp["strings"][ArabolyStringType.NAME][levelNum]
                        developmentsString = " developments: {}".format(", ".join(developmentsList))
                        output = ArabolyGenerals._push_output(channel, context, output, "    \u0003{:02d}${}{} (#{}) -- {},{}".format(playerProp["colourMiRC"], playerProp["price"], mortgagedString, playerProp["field"], playerProp["title"], developmentsString), outputLevel=ArabolyOutputLevel.LEVEL_NODELAY)
                else:
                    output = ArabolyGenerals._push_output(channel, context, output, "{sortedNum: 2d}: {player[name]} at ${player[wallet]}, no properties owned!".format(**locals()), outputLevel=ArabolyOutputLevel.LEVEL_NODELAY)
            output = ArabolyGenerals._push_output(channel, context, output, "Awfom! {playerWinner[name]} has won the game at ${playerWinner[netWorth]} (wallet: ${player[wallet]})!".format(**locals()))
        else:
            output = ArabolyGenerals._push_output(channel, context, output, "Oops! Nobody has won the game!")
        return output
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=0
