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
from ArabolyLogic import ArabolyLogic
from ArabolyMonad import ArabolyMonad
from ArabolyOutput import ArabolyOutput
from ArabolyRules import ArabolyRules
from ArabolyState import ArabolyState
from ArabolyValidate import ArabolyValidate
from sys import argv

class ArabolyIrcBot(object):
    """XXX"""
    commit = daʕat = events = game = ircClient = ircToCommandMap = logic = output = rules = state = validate = None

    #
    # event(self, eventIn): XXX
    def event(self, eventIn):
        return (ArabolyMonad(context=self.game, output=[], status=True, **eventIn) \
                >> self.ircToCommandMap \
                >> self.validate        \
                >> self.daʕat           \
                >> self.logic           \
                >> self.state           \
                >> self.rules           \
                >> self.output          \
                >> self.commit).params["output"]

    #
    # main(argv): XXX
    def main(argv):
        arabolyIrcBot = ArabolyIrcBot(argv)
        while True:
            if arabolyIrcBot.ircClient.connect(15):
                wlist = [] if arabolyIrcBot.ircClient.unqueue() else [arabolyIrcBot.ircClient.clientSocket.fileno()]
                arabolyIrcBot.events.concatSelect(rlist=[arabolyIrcBot.ircClient.clientSocket.fileno()], wlist=wlist)
                if len(wlist):
                    arabolyIrcBot.events.concatSelect(wlist=[arabolyIrcBot.ircClient.clientSocket.fileno()])
                while True:
                    eventsIn = []; eventsOut = []; unqueueFlag = False; wlistFlag = False;
                    readySet = arabolyIrcBot.events.select()
                    if len(readySet[0]) != 0:
                        eventsIn += arabolyIrcBot.ircClient.readlines()
                    eventsIn += arabolyIrcBot.events.timers()
                    for eventIn in eventsIn:
                        eventsOut += arabolyIrcBot.event(eventIn)
                    for eventOut in eventsOut:
                        if eventOut["type"] == "message":
                            arabolyIrcBot.ircClient.queue(eventOut["cmd"], *eventOut["args"])
                            unqueueFlag = True;
                    if unqueueFlag:
                        if not arabolyIrcBot.ircClient.unqueue():
                            arabolyIrcBot.events.concatSelect(wlist=[arabolyIrcBot.ircClient.clientSocket.fileno()])
                        else:
                            arabolyIrcBot.events.filterSelect(wlist=[arabolyIrcBot.ircClient.clientSocket.fileno()])
                arabolyIrcBot.ircClient.close()
            else:
                return False
        return True

    #
    # __init__(self, argv): initialisation method
    def __init__(self, argv):
        defaultArgs = [None, "6667", "ARABOLY", "ARABOLY", "Araboly NT 3.1 Advanced Server", "#ARABOLY"]
        mergedArgs = [*argv[1:] + [defaultArgs[x] for x in range(len(argv[1:]), len(defaultArgs))]]
        self.commit = ArabolyCommit()
        self.daʕat = ArabolyDaʕat()
        self.events = ArabolyEvents()
        self.game = ArabolyGame()
        self.ircClient = ArabolyIrcClient(*mergedArgs[0:5])
        self.ircToCommandMap = ArabolyIrcToCommandMap(clientChannel=mergedArgs[5], clientNick=mergedArgs[2])
        self.logic = ArabolyLogic()
        self.output = ArabolyOutput()
        self.rules = ArabolyRules()
        self.state = ArabolyState()
        self.validate = ArabolyValidate()

if __name__ == "__main__":
    exit(ArabolyIrcBot.main(argv))

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120
