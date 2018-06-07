#!/usr/bin/env python3
#
# Araboly 2000 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from Araboly import Araboly
from ArabolyState import ArabolyState, ArabolyOutputLevel
from getopt import getopt
import copy, os, pdb, sys, yaml

class ArabolyDebugger(Araboly):
    """XXX"""
    gameFieldsFilter = ["auctionState", "board", "clientParams", "players", "state", "tradeState"]
    optionsDefault = {**Araboly.optionsDefault,
        "breakpoint":None, "help":None, "savefile":None, "verbose":False}
    optionsString = "b:f:hv"
    optionsStringMap = {"b":"breakpoint", "f":"savefile", "h":"help", "v":"verbose"}

    # {{{ _diffDict(self, dictNow, dictOld): XXX
    def _diffDict(self, dictNow, dictOld):
        diffString = "{"
        for itemName in dictNow:
            if type(dictNow[itemName]) == dict:
                if itemName not in dictOld:
                    diffString += "\x1b[92m+\x1b[0m" + str(itemName) + ": " + str(dictNow[itemName]) + ", "
                elif dictOld[itemName] != dictNow[itemName]:
                    diffString += str(itemName) + ": " + self._diffDict(dictNow[itemName], dictOld[itemName]) + ", "
            else:
                if itemName not in dictOld:
                    diffString += "\x1b[92m+\x1b[0m" + str(itemName) + ": " + str(dictNow[itemName]) + ", "
                elif dictOld[itemName] != dictNow[itemName]:
                    diffString += "\x1b[91m-\x1b[0m" + str(itemName) + ": " + str(dictOld[itemName]) + ", "
                    diffString += "\x1b[92m+\x1b[0m" + str(itemName) + ": " + str(dictNow[itemName]) + ", "
        return diffString.rstrip(", ") + "}"
    # }}}
    # {{{ _diffState(self, gameNow, gameOld): XXX
    def _diffState(self, gameNow, gameOld):
        diffStringList = []
        for gameField in self.gameFieldsFilter:
            for fieldOld, fieldNow, diffType in [                                                   \
                    [gameNow.__dict__[gameField], gameOld.__dict__[gameField], "\x1b[91m-\x1b[0m"], \
                    [gameOld.__dict__[gameField], gameNow.__dict__[gameField], "\x1b[92m+\x1b[0m"]]:
                if type(fieldNow) == dict:
                    continue
                elif type(fieldNow) == list:
                    raise ValueError
                elif fieldNow != fieldOld:
                    diffStringList += [gameField + ": " + diffType + str(fieldNow)]
            for fieldOld, fieldNow in [                                                             \
                    [gameOld.__dict__[gameField], gameNow.__dict__[gameField]]]:
                if type(fieldNow) == dict and fieldNow != fieldOld:
                    diffStringList += [gameField + ": " + self._diffDict(fieldNow, fieldOld)]
        return diffStringList
    # }}}
    # {{{ _inputRoutine(self, event, testNum, testsLen, breakpoint=None): XXX
    def _inputRoutine(self, event, testNum, testsLen, breakpoint=None):
        eventsOut = []; unqueueFlag = False;
        print("------------------\n")
        print("\x1b[96mINPUT #{}/{}\x1b[0m: <\x1b[4m{}\x1b[0m> {}, {}".format(  \
            testNum, testsLen, event["src"], event["cmd"], str({k:event[k] for k in event if not k in ["cmd", "src"]})))
        if event["eventType"] == "command":
            extras = {"debug":True, "testing":True}
            if breakpoint != None:
                if len(breakpoint) == 3:
                    if breakpoint[2] == testNum:
                        extras["breakpoint"] = breakpoint[:2]
                else: 
                    extras["breakpoint"] = breakpoint
            status, newEventsOut, paramsOut = self.unit(event, **extras)
            eventsOut += newEventsOut
        return eventsOut, paramsOut, unqueueFlag, status
    # }}}
    # {{{ _outputRoutine(self, events, gameOld, params, statusExc, testNum, testsLen): XXX
    def _outputRoutine(self, events, gameOld, params, statusExc, testNum, testsLen):
        for event in events:
            if event["eventType"] != "command":
                continue
            elif not "outputLevel" in event \
            or   event["outputLevel"] != ArabolyOutputLevel.LEVEL_GRAPHICS:
                if not statusExc or not params["status"]:
                    printColour = "91"
                else:
                    printColour = "92"
                print("\x1b[{}mOUTPUT #{}/{}\x1b[0m: {}".format(printColour, testNum, testsLen, event["args"][1]))
        diffStringList = self._diffState(self.typeObjects[ArabolyState], gameOld)
        if len(diffStringList):
            print("\x1b[94mSTATE DIFF #{}/{}\x1b[0m: {}".format(testNum, testsLen, ", ".join(diffStringList)))
        if not params["status"] or not statusExc:
            if not params["status"]:
                print("\x1b[91mERROR #{}/{}\x1b[0m: in {}, monadic value: {}".format(testNum, testsLen, params["failClass"], {k:v for k,v in params.items() if k != "output"}))
            return False
        else:
            return True
    # }}}
    # {{{ synchronise(self): XXX
    def synchronise(self):
        statusExc = True; testsLen = len(self.options["savefile"]); testNum = 0;
        for event in self.options["savefile"]:
            gameOld = copy.deepcopy(self.typeObjects[ArabolyState]); testNum += 1;
            eventsOut, paramsOut, unqueueFlag, statusExc = self._inputRoutine(event, testNum, testsLen, self.options["breakpoint"])
            if not self._outputRoutine(eventsOut, gameOld, paramsOut, statusExc, testNum, testsLen):
                return False
        return statusExc
    # }}}
    # {{{ __init__(self, argv): initialisation method
    def __init__(self, argv):
        options = {}; rc = 0;
        optionsList, args = getopt(argv[1:], self.optionsString)
        for optionChar, optionArg in optionsList:
            optionName = self.optionsStringMap[optionChar[1:]]
            if type(self.optionsDefault[optionName]) == bool:
                options[optionName] = True
            else:
                options[optionName] = optionArg
        if "breakpoint" in options:
            breakpoint = options["breakpoint"].split(":")
            if len(breakpoint) == 2 or len(breakpoint) == 3:
                if not breakpoint[0].startswith("Araboly"):
                    breakpoint[0] = "Araboly" + \
                        breakpoint[0][0].upper() + breakpoing[0][1:]
                if len(breakpoint) == 3:
                    breakpoint[2] = int(breakpoint[2])
                options["breakpoint"] = breakpoint
            else:
                print("error: invalid breakpoint\n", file=sys.stderr); rc = 1;
        if rc != 0 or "help" in options or "savefile" not in options:
            if "savefile" not in options:
                print("error: missing savefile\n", file=sys.stderr); rc = 1;
            with open(os.path.join("assets", "text", "ArabolyDebuggerUsage.txt"), "r") as fileObject:
                for usageLine in fileObject.readlines():
                    print(usageLine.rstrip("\n"), file=sys.stderr)
            exit(rc)
        else:
            with open(options["savefile"], "r") as fileObject:
                options["savefile"] = yaml.load(fileObject)
            super().__init__({**options, "channel":"#arab", "debug":True, "testing":True})
    # }}}

if __name__ == "__main__":
    exit(ArabolyDebugger(sys.argv).synchronise())

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=0
