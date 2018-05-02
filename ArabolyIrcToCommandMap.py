#!/usr/bin/env python3
#
# Araboly NT 4.0 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from ArabolyMonad import ArabolyMonadFunctionDecorator
from ArabolyTypeClass import ArabolyTypeClass
from string import ascii_lowercase
import time

class ArabolyIrcToCommandMap(ArabolyTypeClass):
    """XXX"""

    # {{{ dispatch001(self, output, **params): Dispatch single 001 (RPL_WELCOME)
    def dispatch001(self, output, **params):
        output += [{"type":"message", "delay":0, "cmd":"JOIN", "args":[self.clientChannel]}]
        return {"output":output, **params}
    # }}}
    # {{{ dispatch353(self, args, idFull, src, **params): Dispatch single 353 message from server
    def dispatch353(self, args, idFull, src, **params):
        if args[2].lower() == self.clientChannel.lower():
            for nickSpec in args[3].split(" "):
                if nickSpec[0].lower() not in ascii_lowercase:
                    nickSpec = nickSpec[1:]
                if nickSpec.lower() != idFull[0].lower():
                    self.nickMap[nickSpec] = nickSpec
        return {"args":args, "idFull":idFull, "src":src, **params}
    # }}}
    # {{{ dispatch433(self, args, output, **params): Dispatch single 353 message from server
    def dispatch433(self, args, output, **params):
        output += [{"type":"message", "delay":0, "cmd":"NICK", "args":[args[1] + "_"]}]
        return {"args":args, "output":output, **params}
    # }}}
    # {{{ dispatchJOIN(self, args, context, idFull, output, src, **params): Dispatch single JOIN message from server
    def dispatchJOIN(self, args, context, idFull, output, src, **params):
        if args[0].lower() == self.clientChannel.lower():
            nick = src.split("!")[0].lower()
            if nick == idFull[0].lower():
                for logoLine in context.logoLines:
                    output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[args[0], logoLine.rstrip("\n")]}]
                output += [{"type":"timer", "channel":args[0], "expire":900, "nextExpire":900, "subtype":"attract"}]
                self.clientChannelRejoin = False
            elif nick not in self.nickMap:
                self.nickMap[nick] = nick
        return {"args":args, "context":context, "idFull":idFull, "output":output, "src":src, **params}
    # }}}
    # {{{ dispatchKICK(self, args, idFull, output, **params): Dispatch single KICK message from server
    def dispatchKICK(self, args, idFull, output, **params):
        if  args[0].lower() == self.clientChannel.lower() \
        and args[1].lower() == idFull[0].lower():
            self.clientChannelRejoin = True
            output += [{"type":"message", "delay":time.time() + 15, "cmd":"JOIN", "args":[self.clientChannel]}]
        return {"args":args, "idFull":idFull, "output":output, **params}
    # }}}
    # {{{ dispatchNICK(self, args, idFull, src, **params): Dispatch single NICK message from server
    def dispatchNICK(self, args, idFull, src, **params):
        nick = src.split("!")[0]
        if nick.lower() != idFull[0].lower():
            self.nickMap[args[0]] = self.nickMap[nick]
            del self.nickMap[nick]
        return {"args":args, "idFull":idFull, "src":src, **params}
    # }}}
    # {{{ dispatchPART(self, args, **params): Dispatch single PART message from server
    def dispatchPART(self, args, **params):
        if args[0].lower() == self.clientChannel.lower():
            self.nickMap = {}
        return {"args":args, **params}
    # }}}
    # {{{ dispatchPING(self, args, output, **params): Dispatch single PING message from server
    def dispatchPING(self, args, output, **params):
        output += [{"type":"message", "delay":0, "cmd":"PONG", "args":args}]
        return {"args":args, "output":output, **params}
    # }}}
    # {{{ dispatchPRIVMSG(self, args, context, output, src, **params): Dispatch single PRIVMSG message from server
    def dispatchPRIVMSG(self, args, context, output, src, **params):
        if  args[0].lower() == self.clientChannel.lower()   \
        and args[1].startswith(".m"):
            if context.inhibitUntil > 0:
                if context.inhibitUntil <= time.time():
                    context.inhibitUntil = 0
                else:
                    return {"args":args, "context":context, "output":output, "src":src, **params}
            if args[1].startswith(".melp?"):    # FUCK YOU PYTHON
                params["cmd"] = "melp"          # ARAB <- WON; ARAB <- WINNER
            else:
                params["cmd"] = args[1].split(" ")[0][2:]
            params["channel"] = args[0].lower()
            params["srcFull"] = src
            src = self.nickMap[src.split("!")[0]]
            args = args[1].split(" ")[1:]
            params["type"] = "command"
        return {"args":args, "context":context, "output":output, "src":src, **params}
    # }}}
    # {{{ __init__(self, channel, **kwargs): initialisation method
    def __init__(self, channel, **kwargs):
        self.clientChannel = channel; self.clientChannelRejoin = False; self.nickMap = {};
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120
