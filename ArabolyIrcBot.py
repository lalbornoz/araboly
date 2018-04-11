#!/usr/bin/env python3
#
# Araboly NT 3.1 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from ArabolyCommit import ArabolyCommit
from ArabolyDaʕat import ArabolyDaʕat
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

class ArabolyIrcBot(object):
    """XXX"""
    optsDefault = {"channel":"#ARABOLY", "hostname":None, "nick":"ARABOLY", "port":"6667", "realname":"Araboly NT 3.1 Advanced Server", "user":"ARABOLY"}
    optsMap = {"c":"channel", "h":"help", "H":"hostname", "n":"nick", "p":"port", "r":"realname", "u":"user"}
    optsString = "c:hH:n:p:r:u:"
    typeDict = {}
    typeObjects = [ArabolyCommit, ArabolyDaʕat, ArabolyEvents, ArabolyGame, ArabolyIrcClient, ArabolyIrcToCommandMap, ArabolyLog, ArabolyLogic, ArabolyOutput, ArabolyRules, ArabolyState, ArabolyValidate]

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
                while True:
                    eventsIn = []; eventsOut = []; unqueueFlag = False; wlistFlag = False;
                    readySet = events.select()
                    if len(readySet[0]) != 0:
                        eventsIn += ircClient.readlines()
                    eventsIn += events.timers()
                    for eventIn in eventsIn:
                        if  eventIn["type"] == "timer"  \
                        and "unqueue" in eventIn:
                            for unqueueLine in eventIn["unqueue"]:
                                ircClient.queue(*unqueueLine); unqueueFlag = True;
                            continue
                        game = arabolyIrcBot.typeDict[ArabolyGame]
                        unit = ArabolyMonad(context=game, output=[], status=True, **eventIn)
                        eventsOut += (unit                                          \
                                >> ArabolyIrcBot.typeDict[ArabolyIrcToCommandMap]   \
                                >> ArabolyIrcBot.typeDict[ArabolyValidate]          \
                                >> ArabolyIrcBot.typeDict[ArabolyDaʕat]             \
                                >> ArabolyIrcBot.typeDict[ArabolyLogic]             \
                                >> ArabolyIrcBot.typeDict[ArabolyState]             \
                                >> ArabolyIrcBot.typeDict[ArabolyRules]             \
                                >> ArabolyIrcBot.typeDict[ArabolyOutput]            \
                                >> ArabolyIrcBot.typeDict[ArabolyLog]               \
                                >> ArabolyIrcBot.typeDict[ArabolyCommit]).params["output"]
                    for eventOut in eventsOut:
                        if eventOut["type"] == "message":
                            msg = [eventOut["cmd"], *eventOut["args"]]
                            if eventOut["delay"] == 0:
                                ircClient.queue(*msg); unqueueFlag = True;
                            else:
                                delay = 0.100 if eventOut["delay"] == -1 else eventOut["delay"]
                                events.concatTimers(expire=delay, unqueue=[msg])
                    if unqueueFlag:
                        if not ircClient.unqueue():
                            events.concatSelect(wlist=[ircClient.clientSocket.fileno()])
                        else:
                            events.filterSelect(wlist=[ircClient.clientSocket.fileno()])
                ircClient.close()
            else:
                return False
        return True

    #
    # __new__(self, argv): creation method
    def __new__(self, argv):
        optsList, args = getopt(argv[1:], self.optsString)
        optsDict = {self.optsMap[a[1:]]:b for a,b in optsList}
        opts = self.optsDefault.copy(); opts.update(optsDict);
        if "help" in opts or opts["hostname"] == None:
            if opts["hostname"] == None:
                print("error: missing hostname", file=stderr)
            with open("./assets/ArabolyIrcBot.usage", "r") as fileObject:
                [print(line.rstrip("\n")) for line in fileObject.readlines()]
                return None
        else:
            for typeObject in self.typeObjects:
                self.typeDict[typeObject] = typeObject(**opts)
            return self

if __name__ == "__main__":
    exit(ArabolyIrcBot.main(argv))

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120
