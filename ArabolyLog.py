#!/usr/bin/env python3
#
# Araboly NT 3.1 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from ArabolyTypeClass import ArabolyTypeClass
from datetime import date
from time import time, strftime
from enum import Enum

class ArabolyLogLevel(Enum):
    LOG_INFO      = 0
    LOG_ERROR     = 1
    LOG_WARNING   = 2
    LOG_EXCEPTION = 3
    LOG_DEBUG     = 4

class ArabolyLog(ArabolyTypeClass):
    """XXX"""

    # {{{ dispatch(self, **params): XXX
    def dispatch(self, **params):
        self._log(isOutput=False, **params)
        for outputLine in params["output"] if "output" in params else []:
            self._log(**outputLine)
        return params
    # }}}
    # {{{ dispatchError(self, **params): XXX
    def dispatchError(self, **params):
        self._log(isOutput=False, **params)
        for outputLine in params["output"] if "output" in params else []:
            self._log(ArabolyLogLevel.LOG_ERROR, **outputLine)
        return params
    # }}}
    # {{{ dispatchException(self, e, exc_fname, exc_lineno, exc_stack, **params): XXX
    def dispatchException(self, e, exc_fname, exc_lineno, exc_stack, **params):
        self._log(isOutput=False, **params)
        for outputLine in params["output"] if "output" in params else []:
            self._log(ArabolyLogLevel.LOG_EXCEPTION, **outputLine)
        return {"e":e, "exc_fname":exc_fname, "exc_lineno":exc_lineno, "exc_stack":exc_stack, **params}
    # }}}
    # {{{ _log(self, level=ArabolyLogLevel.LOG_INFO, isOutput=True, **kwargs): XXX
    def _log(self, level=ArabolyLogLevel.LOG_INFO, isOutput=True, **kwargs):
        if "logLevel" in kwargs:
            level = kwargs["logLevel"]
        if level == ArabolyLogLevel.LOG_DEBUG:
            pass
        elif kwargs["type"] == "command":
            ts = date.fromtimestamp(time()).strftime("%d-%b-%Y %H:%M:%S").upper()
            cmd = kwargs["cmd"]; msg = " ".join(kwargs["args"]).rstrip("\n");
            channel = kwargs["channel"]; msg = ": " + msg if len(msg) else "";
            if isOutput:
                print("{} {} Command {} output {} to {}{}".format(ts, ">>>", cmd, channel, msg))
            else:
                src = kwargs["src"].rstrip("!")
                print("{} {} Command {} from {} on {}{}".format(ts, "<<<", cmd, src, channel, msg))
        elif kwargs["type"] == "message":
            ts = date.fromtimestamp(time()).strftime("%d-%b-%Y %H:%M:%S").upper()
            destType = "channel " + kwargs["args"][0] if kwargs["args"][0][0] == "#" else "server"
            cmdType = kwargs["cmd"].upper() + " command"
            msg = " ".join(kwargs["args"][1:]).rstrip("\n")
            msg = ": " + msg if len(msg) else ""
            if isOutput:
                dest = " to " + kwargs["args"][0] if "args" in kwargs else ""
                print("{} {} {} {}{}{}".format(ts, ">>>", destType.title(), cmdType, dest, msg))
            else:
                src = " from " + kwargs["src"].rstrip("!") if "src" in kwargs else ""
                print("{} {} {} {}{}{}".format(ts, "<<<", destType.title(), cmdType, src, msg))
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120
