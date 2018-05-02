#!/usr/bin/env python3
#
# Araboly NT 3.1 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from ArabolyGame import ArabolyGameField, ArabolyGameState
from ArabolyTypeClass import ArabolyTypeClass

class ArabolyCommit(ArabolyTypeClass):
    """XXX"""

    # {{{ dispatch(self, context, **params): XXX
    def dispatch(self, context, **params):
        for param in [p for p in params if p.startswith("new")]:
            paramVarName = param[3].lower() + param[4:]
            if hasattr(context, paramVarName):
                paramVar = getattr(context, paramVarName)
                if type(paramVar) == dict:
                    paramVar.update(params[param])
                elif (type(paramVar) == int or type(paramVar) == str):
                    setattr(context, paramVarName, params[param])
                elif type(paramVar) == list:
                    paramVar += params[param]
                else:
                    setattr(context, paramVarName, params[param])
        for param in [p for p in params if p.startswith("del")]:
            paramVarName = param[3].lower() + param[4:]
            if hasattr(context, paramVarName):
                paramVar = getattr(context, paramVarName)
                if type(paramVar) == dict:
                    [paramVar.pop(param_) for param_ in list(params[param])]
                elif (type(paramVar) == int or type(paramVar) == str):
                    raise TypeError
                elif type(paramVar) == list:
                    [paramVar.remove(param_) for param_ in params[param]]
                else:
                    raise TypeError
        return {"context":context, **params}
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120
