#!/usr/bin/env python3
#
# Araboly 2000 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from ArabolyAttractMode import ArabolyAttractMode
from ArabolyMonad import ArabolyDecorator
from ArabolyState import ArabolyGameState
from ArabolyTypeClass import ArabolyTypeClass
from string import ascii_lowercase
import time

@ArabolyDecorator()
class ArabolyIrcToCommandMap(ArabolyTypeClass):
    """XXX"""
    commandsFilter = [
        "accept", "bid", "board", "buy", "cheat", "develop", "dice",
        "help", "join", "kick", "lift", "melp", "mortgage", "part",
        "pass", "reject", "sell", "start", "status", "stop"]

    # {{{ dispatch001(context, output): Dispatch single 001 (RPL_WELCOME)
    @staticmethod
    def dispatch001(context, output):
        output += [{"eventType":"message", "delay":0, "cmd":"JOIN", "args":[context.clientParams["channel"]]}]
        return context, output
    # }}}
    # {{{ dispatch353(args, context, idFull): Dispatch single 353 message from server
    @staticmethod
    def dispatch353(args, context, idFull):
        if args[2].lower() == context.clientParams["channel"].lower():
            for nickSpec in args[3].split(" "):
                if nickSpec[0].lower() not in ascii_lowercase:
                    nickSpec = nickSpec[1:]
                if nickSpec.lower() != idFull[0].lower():
                    context.clientParams["nickMap"][nickSpec] = nickSpec
        return args, context, idFull
    # }}}
    # {{{ dispatch433(args, output): Dispatch single 353 message from server
    @staticmethod
    def dispatch433(args, output):
        output += [{"eventType":"message", "delay":0, "cmd":"NICK", "args":[args[1] + "_"]}]
        return args, output
    # }}}
    # {{{ dispatchJOIN(args, context, idFull, output, src): Dispatch single JOIN message from server
    @staticmethod
    def dispatchJOIN(args, context, idFull, output, src):
        if args[0].lower() == context.clientParams["channel"].lower():
            nick = src.split("!")[0].lower()
            if nick == idFull[0].lower():
                context.clientParams["channelRejoin"] = False
                if context.state == ArabolyGameState.ATTRACT:
                    output = ArabolyAttractMode._enter(args[0], context, output)
            elif nick not in context.clientParams["nickMap"]:
                context.clientParams["nickMap"][nick] = nick
        return args, context, idFull, output, src
    # }}}
    # {{{ dispatchKICK(args, context, idFull, output): Dispatch single KICK message from server
    @staticmethod
    def dispatchKICK(args, context, idFull, output):
        if  args[0].lower() == context.clientParams["channel"].lower()  \
        and args[1].lower() == idFull[0].lower():
            context.clientParams["channelRejoin"] = True
            output += [{"eventType":"message", "delay":time.time() + 15, "cmd":"JOIN", "args":[context.clientParams["channel"]]}]
        return args, context, idFull, output
    # }}}
    # {{{ dispatchNICK(args, context, idFull, src): Dispatch single NICK message from server
    @staticmethod
    def dispatchNICK(args, context, idFull, src):
        nick = src.split("!")[0]
        if nick not in context.clientParams["nickMap"]:
            context.clientParams["nickMap"][nick] = nick
        elif nick.lower() != idFull[0].lower():
            context.clientParams["nickMap"][args[0]] = context.clientParams["nickMap"][nick]
            del context.clientParams["nickMap"][nick]
        return args, context, idFull, src
    # }}}
    # {{{ dispatchPART(args, context): Dispatch single PART message from server
    @staticmethod
    def dispatchPART(args, context):
        if args[0].lower() == context.clientParams["channel"].lower():
            context.clientParams["nickMap"] = {}
        return args, context
    # }}}
    # {{{ dispatchPING(args, output): Dispatch single PING message from server
    @staticmethod
    def dispatchPING(args, output):
        output += [{"eventType":"message", "delay":0, "cmd":"PONG", "args":args}]
        return args, output
    # }}}
    # {{{ dispatchPRIVMSG(args, context, output, src, status, channel=None, cmd=None, eventType=None, srcFull=None): Dispatch single PRIVMSG message from server
    @staticmethod
    def dispatchPRIVMSG(args, context, output, src, status, channel=None, cmd=None, eventType=None, srcFull=None):
        srcList = src.split("!")
        if len(srcList) == 2:
            srcList = [srcList[0], *srcList[1].split("@")]
        if  args[0].lower() == context.clientParams["channel"].lower()  \
        and args[1].startswith(".m"):
            if context.clientParams["inhibitUntil"] > 0:
                if context.clientParams["inhibitUntil"] <= time.time():
                    context.clientParams["inhibitUntil"] = 0
                else:
                    return args, context, output, src, status, channel, cmd, eventType, srcFull
            if args[1].startswith(".melp?"):    # FUCK YOU PYTHON
                cmd = "melp"          # ARAB <- WON; ARAB <- WINNER
            else:
                cmd = args[1].split(" ")[0][2:]
            if cmd in ArabolyIrcToCommandMap.commandsFilter:
                channel = args[0].lower()
                srcFull = src
                if srcList[0] not in context.clientParams["nickMap"]:
                    context.clientParams["nickMap"][srcList[0]] = srcList[0]
                src = context.clientParams["nickMap"][srcList[0]]
                args = args[1].split(" ")[1:]
                eventType = "command"
            else:
                status = False
        return args, context, output, src, status, channel, cmd, eventType, srcFull
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=0
