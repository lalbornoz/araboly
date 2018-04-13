#!/usr/bin/env python3
#
# Araboly NT 3.1 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from ArabolyTypeClass import ArabolyTypeClass
import os, sys, traceback

class ArabolyMonad(object):
    """ما أملح العساكر * وترتيب الصفوف"""
    params = None

    # {{{ bind(self, other): XXX
    def bind(self, other):
        if callable(other):
            params = other(**self.params)
        elif isinstance(other, ArabolyTypeClass):
            select = ""
            if not self.params["status"]:
                if "e" in self.params:
                    select = "dispatchException"
                else:
                    select = "dispatchError"
            elif "dispatch" in other.__class__.__dict__:
                select = "dispatch"
            elif self.params["type"] == "command":
                select = "dispatch_" + self.params["cmd"].lower()
            elif self.params["type"] == "message":
                select = "dispatch" + self.params["cmd"].upper()
            elif self.params["type"] == "timer":
                select = "dispatchTimer"
            if select in other.__class__.__dict__:
                try:
                    params = getattr(other, select)(**self.params)
                except:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    if exc_type == KeyboardInterrupt:
                        raise exc_obj
                    else:
                        self.params["failClass"] = str(other.__class__)
                        self.params["exc_obj"] = exc_obj; self.params["exc_type"] = exc_type;
                        self.params["exc_fname"] = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        self.params["exc_lineno"] = exc_tb.tb_lineno
                        self.params["exc_stack"] = "\n".join(traceback.format_stack()).split("\n")
                        self.params["status"] = False
                        if hasattr(other, "dispatchException"):
                            params = getattr(other, "dispatchException")(**self.params)
                        else:
                            params = self.params
                if not params["status"]:
                    params["failClass"] = str(other.__class__)
            else:
                params = self.params
        else:
            params = other
        return self.unit(**params)
    # }}}
    # {{{ unit(self, **other): XXX
    def unit(self, **other):
        self.params = other; return self;
    # }}}
    # {{{ __init__(self, **kwargs): initialisation method
    def __init__(self, **kwargs):
        self.unit(**kwargs)
    # }}}
    # {{{ __rshift__(self, other): XXX
    def __rshift__(self, other):
        return self.bind(other)
    # }}}

def ArabolyMonadFunctionDecorator(function):
    """بالمعلم المشوف * على الوتر الفصيح"""

    def ArabolyMonadFunctionDecoratorOuter(*argsOuter):
        def ArabolyMonadFunctionDecoratorInner(*argsInner):
            return function(*argsOuter, *argsInner)
        return ArabolyMonadFunctionDecoratorInner
    return ArabolyMonadFunctionDecoratorOuter

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120
