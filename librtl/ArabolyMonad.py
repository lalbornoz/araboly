#!/usr/bin/env python3
#
# Araboly 2000 Advanced Server SP4 -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from ArabolyTypeClass import ArabolyTypeClass
import bdb, inspect, os, pdb, sys, traceback

class ArabolyMonad(object):
    """ما أملح العساكر * وترتيب الصفوف"""

    # {{{ bind(self, other): XXX
    def bind(self, other):
        if issubclass(other, ArabolyTypeClass):
            if hasattr(other, "matchDict"):
                for matchParam, matchList in other.matchDict.items():
                    for matchKey, matchValue in matchList.items():
                        if getattr(self.params[matchParam], matchKey) != matchValue:
                            return self.unit(**self.params)
            select = ""
            if not self.params["status"]:
                if "exc_obj" in self.params:
                    select = "dispatchException"
                else:
                    select = "dispatchError"
            elif "dispatch" in other.__dict__:
                select = "dispatch"
            elif self.params["eventType"] == "command":
                select = "dispatch_" + self.params["cmd"].lower()
            elif self.params["eventType"] == "message":
                select = "dispatch" + self.params["cmd"].upper()
            elif self.params["eventType"] == "timer":
                select = "dispatchTimer"
            if  select in other.__dict__                                \
            and not "hasDispatch" in self.params:
                if self.params["eventType"] == "command":
                    self.params["hasDispatch"] = True
                try:
                    fun, params = getattr(other, select), self.params
                    funArgs = inspect.signature(fun).parameters
                    funArgsDict = {p:params[p] for p in params.keys() if p in funArgs and funArgs[p].default == inspect.Parameter.empty}
                    if  "breakpoint" in self.params                     \
                    and self.params["breakpoint"][0] == other.__name__  \
                    and self.params["breakpoint"][1] == select:
                        pdb.set_trace()
                    paramsOut, numParamOut = fun(**funArgsDict), 0
                    for funArg in funArgs:
                        params[funArg] = paramsOut[numParamOut]
                        numParamOut += 1
                except:
                    params = self._error(other, self.params)
                if not params["status"]:
                    params["failClass"] = other.__name__
            else:
                params = self.params
        else:
            raise ValueError
        return self.unit(**params)
    # }}}
    # {{{ unit(self, **other): XXX
    def unit(self, **other):
        self.params = other; return self;
    # }}}
    # {{{ _error(self, other, params): XXX
    def _error(self, other, params):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        if exc_type == KeyboardInterrupt:
            raise exc_obj
        elif exc_type == SystemExit:
            raise exc_obj
        elif exc_type == bdb.BdbQuit:
            exit(1)
        else:
            self.params["failClass"] = other.__name__
            self.params["exc_obj"] = exc_obj; self.params["exc_type"] = exc_type;
            tb_last = exc_tb
            while tb_last.tb_next != None:
                tb_last = tb_last.tb_next
            self.params["exc_fname"] = os.path.split(tb_last.tb_frame.f_code.co_filename)[1]
            self.params["exc_lineno"] = tb_last.tb_lineno
            self.params["exc_stack"] = "\n".join(traceback.format_tb(exc_tb)).split("\n")
            if "debug" in self.params:
                print("Traceback (most recent call last):", file=sys.stderr)
                print("\n".join(params["exc_stack"]), file=sys.stderr)
                print("\x1b[91m{} exception in {}:{}\x1b[0m: \x1b[4m{}\x1b[0m".format(str(params["exc_type"]), params["exc_fname"], params["exc_lineno"], str(params["exc_obj"])), file=sys.stderr)
                print("Monadic value: {}".format({k:v for k,v in params.items() if k != "output"}), file=sys.stderr)
            del exc_tb
            self.params["status"] = False
            if hasattr(other, "dispatchException"):
                params = getattr(other, "dispatchException")(**self.params)
            else:
                params = self.params
        if  not params["status"]    \
        and "failClass" not in params:
            params["failClass"] = other.__name__
        return params
    # }}}
    # {{{ __rshift__(self, other): XXX
    def __rshift__(self, other):
        return self.bind(other)
    # }}}
    # {{{ __init__(self, **kwargs): initialisation method
    def __init__(self, **kwargs):
        self.unit(**kwargs)
    # }}}

def ArabolyDecorator(**matchDict):
    """بالمعلم المشوف * على الوتر الفصيح"""

    def ArabolyDecoratorOuter(targetObject):
        if type(targetObject) == type(object):
            setattr(targetObject, "matchDict", matchDict)
            return targetObject
        elif callable(targetObject): 
            def ArabolyDecoratorInner(**argsInner):
                setattr(targetObject, "matchDict", matchDict)
                return targetObject(**argsInner)
            return ArabolyDecoratorInner
    return ArabolyDecoratorOuter

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=0
