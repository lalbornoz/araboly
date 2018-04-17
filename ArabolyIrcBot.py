#!/usr/bin/env python3
#
# Araboly NT 3.1 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from ArabolyCommit import ArabolyCommit
from ArabolyDaʕat import ArabolyDaʕat
from ArabolyErrors import ArabolyErrors
from ArabolyEvents import ArabolyEvents
from ArabolyGame import ArabolyGame
from ArabolyIrcClient import ArabolyIrcClient
from ArabolyIrcToCommandMap import ArabolyIrcToCommandMap
from ArabolyLog import ArabolyLog
from ArabolyLogic import ArabolyLogic
from ArabolyMonad import ArabolyMonad
from ArabolyOutput import ArabolyOutput
from ArabolyRules import ArabolyRules
from ArabolyState import ArabolyState
from ArabolyValidate import ArabolyValidate
from getopt import getopt
from sys import argv, stderr
import copy, pickle, os

class ArabolyIrcBot(object):
    """XXX"""
    optsDefault = {"channel":"#ARABOLY", "debug":False, "hostname":None, "nick":"ARABOLY", "port":"6667", "realname":"Araboly NT 3.1 Advanced Server", "ssl":False, "user":"ARABOLY"}
    optsMap = {"c":"channel", "d":"debug", "h":"help", "H":"hostname", "n":"nick", "p":"port", "r":"realname", "S":"ssl", "u":"user"}
    optsString = "c:dhH:n:p:r:Su:"
    typeObjects = [ArabolyCommit, ArabolyDaʕat, ArabolyErrors, ArabolyEvents, ArabolyGame, ArabolyIrcClient, ArabolyIrcToCommandMap, ArabolyLog, ArabolyLogic, ArabolyOutput, ArabolyRules, ArabolyState, ArabolyValidate]

    #
    # main(argv): XXX
    def main(argv):
        arabolyIrcBot = ArabolyIrcBot(argv)
        if arabolyIrcBot == None:
            return 0
        while True:
            events = arabolyIrcBot.typeDict[ArabolyEvents]
            ircClient = arabolyIrcBot.typeDict[ArabolyIrcClient]
            if ircClient.connect(15):
                wlist = [] if ircClient.unqueue() else [ircClient.clientSocket.fileno()]
                events.concatSelect(rlist=[ircClient.clientSocket.fileno()], wlist=wlist)
                if len(wlist):
                    events.concatSelect(wlist=[ircClient.clientSocket.fileno()])
                if  arabolyIrcBot.options["debug"]                                   \
                and os.path.isfile("./ArabolyIrcBot.snapshot"):
                    with open("./ArabolyIrcBot.snapshot", "rb") as fileObject:
                        print("Loading game snapshot from ./ArabolyIrcBot.snapshot")
                        arabolyIrcBot.typeDict[ArabolyGame] = pickle.load(fileObject)
                while True:
                    eventsIn = []; eventsOut = []; unqueueFlag = False; wlistFlag = False;
                    readySet = events.select()
                    if len(readySet[0]) != 0:
                        eventsIn += ircClient.readlines()
                    eventsIn += events.timers()
                    for eventIn in eventsIn:
                        if  eventIn["type"] == "timer"                              \
                        and "unqueue" in eventIn:
                            for unqueueLine in eventIn["unqueue"]:
                                ircClient.queue(**unqueueLine); unqueueFlag = True;
                            continue
                        if arabolyIrcBot.options["debug"]:
                            gameSnapshot = copy.deepcopy(arabolyIrcBot.typeDict[ArabolyGame])
                        game = arabolyIrcBot.typeDict[ArabolyGame]
                        unit = ArabolyMonad(context=game, output=[], status=True, **eventIn)
                        unit = unit                                                 \
                                >> ArabolyIrcBot.typeDict[ArabolyIrcToCommandMap]   \
                                >> ArabolyIrcBot.typeDict[ArabolyValidate]          \
                                >> ArabolyIrcBot.typeDict[ArabolyDaʕat]             \
                                >> ArabolyIrcBot.typeDict[ArabolyLogic]             \
                                >> ArabolyIrcBot.typeDict[ArabolyState]             \
                                >> ArabolyIrcBot.typeDict[ArabolyRules]             \
                                >> ArabolyIrcBot.typeDict[ArabolyOutput]            \
                                >> ArabolyIrcBot.typeDict[ArabolyLog]               \
                                >> ArabolyIrcBot.typeDict[ArabolyCommit]            \
                                >> ArabolyIrcBot.typeDict[ArabolyErrors]
                        eventsOut += unit.params["output"]
                    for eventOut in eventsOut:
                        if eventOut["type"] == "message":
                            msg = {k:eventOut[k] for k in eventOut if k == "args" or k == "cmd"}
                            if eventOut["delay"] == 0:
                                ircClient.queue(**msg); unqueueFlag = True;
                            else:
                                delay = 0.100 if eventOut["delay"] == -1 else eventOut["delay"]
                                events.concatTimers(expire=delay, unqueue=[msg])
                        elif eventOut["type"] == "timer":
                            events.concatTimers(**eventOut)
                    if unqueueFlag:
                        if not ircClient.unqueue():
                            events.concatSelect(wlist=[ircClient.clientSocket.fileno()])
                        else:
                            events.filterSelect(wlist=[ircClient.clientSocket.fileno()])
                    if "exc_obj" in unit.params:
                        if arabolyIrcBot.options["debug"]:
                            with open("./ArabolyIrcBot.snapshot", "wb+") as fileObject:
                                print("Saving pre-exception game snapshot to ./ArabolyIrcBot.snapshot")
                                pickle.dump(gameSnapshot, fileObject)
                        return False
                ircClient.close()
            else:
                return False
        return True

    #
    # __new__(self, argv): creation method
    def __new__(self, argv):
        optsList, args = getopt(argv[1:], self.optsString)
        optsDict = {self.optsMap[a[1:]]:b for a,b in optsList}
        optsDict["debug"] = True if "debug" in optsDict else False
        optsDict["ssl"] = True if "ssl" in optsDict else False
        if optsDict["ssl"] and "port" not in optsDict:
            optsDict["port"] = "6697"
        opts = self.optsDefault.copy(); opts.update(optsDict);
        if "help" in opts or opts["hostname"] == None:
            if opts["hostname"] == None:
                print("error: missing hostname", file=stderr)
            with open("./assets/ArabolyIrcBot.usage", "r") as fileObject:
                [print(line.rstrip("\n")) for line in fileObject.readlines()]
                return None
        else:
            self.options = opts; self.typeDict = {};
            for typeObject in self.typeObjects:
                self.typeDict[typeObject] = typeObject(**self.options)
            return self

if __name__ == "__main__":
    exit(ArabolyIrcBot.main(argv))

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120
