#!/usr/bin/env python3
#
# Araboly 2000 Advanced Server SP4 -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from ArabolyGenerals import ArabolyGenerals
from ArabolyMonad import ArabolyDecorator
from ArabolyTypeClass import ArabolyTypeClass
from ArabolyState import ArabolyGameState, ArabolyOutputLevel, ArabolyStringType
from ArabolyTrade import ArabolyTrade
import copy, os, sys, yaml

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
            output = ArabolyGenerals._board(channel, context, output, src)
        return args, channel, context, output, src, status
    # }}}
    # {{{ dispatch_bugcheck(channel, context, srcFull, status): XXX
    @staticmethod
    def dispatch_bugcheck(channel, context, srcFull, status):
        if not ArabolyGenerals._authorised(channel, context, srcFull):
            status = False
        else:
            snapshotPath = os.path.join("savefiles", "snapshot.dmp.{}".format(context.clientParams["hostname"]))
            print("Saving game snapshot to {}!".format(os.path.join("savefiles", snapshotPath)))
            with open(snapshotPath, "w+") as fileObject:
                yaml.dump(context, fileObject)
            sys.exit(1)
        return channel, context, srcFull, status
    # }}}
    # {{{ dispatch_help(channel, context): XXX
    @staticmethod
    def dispatch_help(channel, context, output):
        for helpLine in context.graphics["help"]:
            output = ArabolyGenerals._push_output(channel, context, output, helpLine, outputLevel=ArabolyOutputLevel.LEVEL_GRAPHICS)
        return channel, context, output
    # }}}
    # {{{ dispatch_join(args, channel, context, output, src, status): XXX
    @staticmethod
    def dispatch_join(args, channel, context, output, src, status):
        if  context.state != ArabolyGameState.GAME          \
        and context.state != ArabolyGameState.SETUP:
            status = False
        elif src in context.players["byName"]               \
        or   len(args):
            status = False
        else:
            newNum = None
            for otherNum in range(len(context.players["numMap"])):
                if context.players["numMap"][otherNum] == None:
                    newNum = otherNum; break;
            if newNum == None:
                status = False
            else:
                context.players["byName"][src] = {"field":0, "name":src, "num":newNum, "properties":[], "wallet":1500}
                context.players["numMap"][newNum] = src
                output = ArabolyGenerals._push_output(channel, context, output, "Player {src} joins Araboly game!".format(**locals()))
                if  context.state == ArabolyGameState.SETUP \
                and len([n for n in context.players["numMap"] if n == None]) == 0:
                    output = ArabolyGenerals._push_output(channel, context, output, "Araboly game with {} players has started!".format(len(context.players["numMap"])))
                    output = ArabolyGenerals._push_output(channel, context, output, "{numMap[0]}: roll the dice!".format(**context.players))
                    context.players["curNum"] = 0
                    context.state = ArabolyGameState.GAME
        return args, channel, context, output, src, status
    # }}}
    # {{{ dispatch_kick(args, channel, context, output, srcFull, status): XXX
    @staticmethod
    def dispatch_kick(args, channel, context, output, srcFull, status):
        if context.state == ArabolyGameState.GAME   \
        or context.state == ArabolyGameState.SETUP:
            if len(args) != 1 or len(args[0]) < 1   \
            or args[0] not in context.players["byName"]:
                status = False
            elif ArabolyGenerals._authorised(channel, context, srcFull):
                otherPlayers = [args[0]]
                output = ArabolyGenerals._push_output(channel, context, output, "Kicking {args[0]} from current Araboly game!".format(**locals()))
                context, output = ArabolyGenerals._remove_players(channel, context, output, otherPlayers)
        else:
            status = False
        return args, channel, context, output, srcFull, status
    # }}}
    # {{{ dispatch_melp(channel, context, output): XXX
    @staticmethod
    def dispatch_melp(channel, context, output):
        for explosionLine in context.graphics["explosion"]:
            output = ArabolyGenerals._push_output(channel, context, output, explosionLine, outputLevel=ArabolyOutputLevel.LEVEL_GRAPHICS)
        output = ArabolyGenerals._push_output(channel, context, output, "\u0001ACTION explodes.\u0001", outputLevel=ArabolyOutputLevel.LEVEL_GRAPHICS)
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
                output = ArabolyGenerals._push_output(channel, context, output, "Player {src} parts Araboly game!".format(**locals()))
                context, output = ArabolyGenerals._remove_players(channel, context, output, otherPlayers)
        else:
            status = False
        return args, channel, context, output, src, status
    # }}}
    # {{{ dispatch_save(args, channel, context, output, srcFull, status): XXX
    def dispatch_save(args, channel, context, output, srcFull, status):
        if  context.state != ArabolyGameState.AUCTION       \
        and context.state != ArabolyGameState.BANKRUPTCY    \
        and context.state != ArabolyGameState.GAME          \
        and context.state != ArabolyGameState.PROPERTY:
            status = False
        elif len(args) != 1                                 \
        or not ArabolyGenerals._authorised(channel, context, srcFull):
            status = False
        else:
            snapshotPath = os.path.join("savefiles", os.path.basename(args[0]))
            output = ArabolyGenerals._push_output(channel, context, output, "Saving snapshot to {snapshotPath}!".format(**locals()))
            with open(snapshotPath, "w") as fileObject:
                gameSnapshot = copy.deepcopy(context)
                delattr(gameSnapshot, "clientParams")
                delattr(gameSnapshot, "graphics")
                delattr(gameSnapshot, "kades")
                yaml.dump(gameSnapshot, fileObject)
            output = ArabolyGenerals._push_output(channel, context, output, "Saved snapshot to {snapshotPath}!".format(**locals()))
        return args, channel, context, output, srcFull, status
    # }}}
    # {{{ dispatch_status(args, channel, context, output, src, status): XXX
    def dispatch_status(args, channel, context, output, src, status):
        if  context.state != ArabolyGameState.AUCTION       \
        and context.state != ArabolyGameState.BANKRUPTCY    \
        and context.state != ArabolyGameState.GAME          \
        and context.state != ArabolyGameState.PROPERTY:
            status = False
        elif len(args) == 0:
            statusPlayer = src
        elif len(args) == 1:
            statusPlayer = args[0]
        if not statusPlayer in context.players["byName"].keys():
            status = False
        else:
            playerField = context.board[context.players["byName"][statusPlayer]["field"]]
            playerProps = context.players["byName"][statusPlayer]["properties"]
            playerWallet = context.players["byName"][statusPlayer]["wallet"]
            output = ArabolyGenerals._push_output(channel, context, output, "Araboly status for player {statusPlayer}:".format(**locals()), outputLevel=ArabolyOutputLevel.LEVEL_NODELAY)
            output = ArabolyGenerals._push_output(channel, context, output, "Field....: {playerField[title]}".format(**locals()), outputLevel=ArabolyOutputLevel.LEVEL_NODELAY)
            output = ArabolyGenerals._push_output(channel, context, output, "Wallet...: ${playerWallet}".format(**locals()), outputLevel=ArabolyOutputLevel.LEVEL_NODELAY)
            if len(playerProps):
                output = ArabolyGenerals._push_output(channel, context, output, "Properties owned:", outputLevel=ArabolyOutputLevel.LEVEL_NODELAY)
                for playerPropNum in playerProps:
                    playerProp = context.board[playerPropNum]
                    mortgagedString = " (\u001fMORTGAGED\u001f)" if playerProp["mortgaged"] else ""
                    developmentsList = []
                    for levelNum in range(playerProp["level"] + 1):
                        developmentsList += playerProp["strings"][ArabolyStringType.NAME][levelNum]
                    developmentsString = ", level {}, developments: {}".format(playerProp["level"], ", ".join(developmentsList))
                    output = ArabolyGenerals._push_output(channel, context, output, "\u0003{:02d}${}{} (#{}) -- {}{}".format(playerProp["colourMiRC"], playerProp["price"], mortgagedString, playerProp["field"], playerProp["title"], developmentsString), outputLevel=ArabolyOutputLevel.LEVEL_NODELAY)
            output = ArabolyTrade._status(channel, context, output, statusPlayer)
            output = ArabolyGenerals._push_output(channel, context, output, "Current turn: {}".format(context.players["numMap"][context.players["curNum"]]), outputLevel=ArabolyOutputLevel.LEVEL_NODELAY)
        return args, channel, context, output, src, status
    # }}}
    # {{{ dispatch_stop(args, channel, context, output, src, srcFull, status): XXX
    @staticmethod
    def dispatch_stop(args, channel, context, output, src, srcFull, status):
        if context.state == ArabolyGameState.AUCTION    \
        or context.state == ArabolyGameState.BANKRUPTCY \
        or context.state == ArabolyGameState.GAME       \
        or context.state == ArabolyGameState.PROPERTY   \
        or context.state == ArabolyGameState.SETUP:
            if len(args) > 0:
                status = False
            elif ArabolyGenerals._authorised(channel, context, srcFull):
                otherPlayers = list(context.players["byName"].keys())
                context, output = ArabolyGenerals._remove_players(channel, context, output, otherPlayers)
        else:
            status = False
        return args, channel, context, output, src, srcFull, status
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=0
