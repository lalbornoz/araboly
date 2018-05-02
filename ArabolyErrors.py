#!/usr/bin/env python3
#
# Araboly NT 4.0 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from ArabolyTypeClass import ArabolyTypeClass
from sys import stderr

class ArabolyErrors(ArabolyTypeClass):
    """XXX"""

    # {{{ dispatchError(self, output, **params): XXX
    def dispatchError(self, output, **params):
        if params["type"] == "command":
            if "channel" in params:
                output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[params["channel"], "Oh no! arab can't be bothered to write error messages!"]}]
                output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[params["channel"], "Monadic value: {}".format(str(params))]}]
                return {"output":output, **params}
        return {"output":output, **params}
    # }}}
    # {{{ dispatchException(self, exc_fname, exc_lineno, exc_obj, exc_type, exc_stack, output, **params): XXX
    def dispatchException(self, exc_fname, exc_lineno, exc_obj, exc_type, exc_stack, output, **params):
        channel = None
        if   params["type"] == "command"            \
        and  "channel" in params:
            channel = params["channel"]
        elif params["type"] == "message":
            if params["cmd"].upper() == "PRIVMSG"   \
            or params["cmd"].upper() == "NOTICE":
                channel = params["args"][0]
        if channel != None:
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Traceback (most recent call last):"]}]
            for stackLine in exc_stack:
                output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, stackLine]}]
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "{} exception in {}:{}: {}".format(str(exc_type), exc_fname, exc_lineno, str(exc_obj))]}]
            output += [{"type":"message", "delay":0, "cmd":"PRIVMSG", "args":[channel, "Monadic value: {}".format(str(params))]}]
        print("Traceback (most recent call last):", file=stderr)
        print("\n".join(exc_stack), file=stderr)
        print("{} exception in {}:{}: {}".format(str(exc_type), exc_fname, exc_lineno, str(exc_obj)), file=stderr)
        print("Monadic value: {}".format(str(params)), file=stderr)
        return {"exc_fname":exc_fname, "exc_lineno":exc_lineno, "exc_obj":exc_obj, "exc_type":exc_type, "exc_stack":exc_stack, "output":output, **params}
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120
