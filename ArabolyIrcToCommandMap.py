#!/usr/bin/env python3
#
# Araboly NT 3.1 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from ArabolyMonad import ArabolyMonadFunctionDecorator
from ArabolyTypeClass import ArabolyTypeClass

class ArabolyIrcToCommandMap(ArabolyTypeClass):
    """XXX"""
    clientChannel = None; clientChannelRejoin = False; clientNick = "";

    # {{{ dispatch001(self, output, **params): Dispatch single 001 (RPL_WELCOME)
    def dispatch001(self, output, **params):
        output += [{"type":"message", "delay":-1, "cmd":"JOIN", "args":[self.clientChannel]}]
        return {"output":output, **params}
    # }}}
    # {{{ dispatchJOIN(self, args, **params): Dispatch single JOIN message from server
    def dispatchJOIN(self, args, **params):
        if args[0].lower() == self.clientChannel.lower():
            self.clientChannelRejoin = False
        return {"args":args, **params}
    # }}}
    # {{{ dispatchKICK(self, args, output, **params): Dispatch single KICK message from server
    def dispatchKICK(self, args, output, **params):
        if  args[0].lower() == self.clientChannel.lower() \
        and args[1].lower() == self.clientNick.lower():
            self.clientChannelRejoin = True
            output += {"type":"message", "delay":time.time() + 15, "cmd":"JOIN", "args":[self.clientChannel]}
        return {"args":args, "output":output, **params}
    # }}}
    # {{{ dispatchPING(self, args, output, **params): Dispatch single PING message from server
    def dispatchPing(self, args, output, **params):
        output += {"type":"message", "delay":-1, "cmd":"PONG", "args":args}
        return {"args":args, "output":output, **params}
    # }}}
    # {{{ dispatchPRIVMSG(self, args, output, **params): Dispatch single PRIVMSG message from server
    def dispatchPRIVMSG(self, args, output, **params):
        if  args[0].lower() == self.clientChannel.lower()   \
        and args[1].startswith(".m"):
            params["cmd"] = args[1].split(" ")[0][2:]
            params["channel"] = args[0].lower()
            args = args[1].split(" ")[1:]
            params["type"] = "command"
        return {"args":args, "output":output, **params}
    # }}}
    # {{{ __init__(self, channel, nick, **kwargs): initialisation method
    def __init__(self, channel, nick, **kwargs):
        self.clientChannel = channel; self.clientNick = nick;
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120
