#!/usr/bin/env python3
#
# Araboly 2000 Advanced Server SP3 -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from Araboly import Araboly
from ArabolyEvents import ArabolyEvents
from ArabolyIrcClient import ArabolyIrcClient
from ArabolyState import ArabolyOutputLevel, ArabolyState
from datetime import datetime
from getopt import getopt
from time import strftime
import copy, os, sys, time, yaml

class ArabolyIrcBot(Araboly):
    """XXX"""
    optionsDefault = {**Araboly.optionsDefault,
        "channel":"#ARABOLY", "connect_timeout":15, "debug":False,
        "flood_delay":0, "help":None, "hostname":None, "nick":"ARABOLY",
        "port":"6667", "realname":"Araboly 2000 Advanced Server SP3",
        "recording":False, "snapshot_path":"savefiles/snapshot.dmp",
        "ssl":False, "user":"ARABOLY"}
    optionsString = "b:c:C:df:hH:n:p:r:RSt:u:"
    optionsStringMap = {
        "c":"channel", "C":"connect_timeout", "d":"debug",
        "f":"flood_delay", "h":"help", "H":"hostname", "n":"nick",
        "p":"port", "r":"realname", "R":"recording", "S":"ssl", "u":"user"}
    typeObjects = [*Araboly.typeObjects, ArabolyEvents, ArabolyIrcClient]

    # {{{ _errorRoutine(self, eventsOut, paramsOut, status): XXX
    def _errorRoutine(self, eventsOut, paramsOut, status):
        if not status:
            eventsOut += [{"eventType":"message", "delay":0, "cmd":"PRIVMSG", "args":[paramsOut["context"].clientParams["channel"], "Traceback (most recent call last):"]}]
            for stackLine in paramsOut["exc_stack"]:
                eventsOut += [{"eventType":"message", "delay":0, "cmd":"PRIVMSG", "args":[paramsOut["context"].clientParams["channel"], stackLine]}]
            eventsOut += [{"eventType":"message", "delay":0, "cmd":"PRIVMSG", "args":[paramsOut["context"].clientParams["channel"], "{} exception in {}:{}: {}".format(str(paramsOut["exc_type"]), paramsOut["exc_fname"], paramsOut["exc_lineno"], str(paramsOut["exc_obj"]))]}]
            eventsOut += [{"eventType":"message", "delay":0, "cmd":"PRIVMSG", "args":[paramsOut["context"].clientParams["channel"], "Monadic value: {}".format({k:v for k,v in paramsOut.items() if k != "output"})]}]
            status = True
        elif not paramsOut["status"]:
            eventsOut += [{"eventType":"message", "delay":0, "cmd":"PRIVMSG", "args":[paramsOut["context"].clientParams["channel"], "Oh no! arab can't be bothered to write error messages!"]}]
            eventsOut += [{"eventType":"message", "delay":0, "cmd":"PRIVMSG", "args":[paramsOut["context"].clientParams["channel"], "Monadic value: {}".format({k:v for k,v in paramsOut.items() if k != "output"})]}]
            status = True
        return eventsOut, status
    # }}}
    # {{{ _inputRoutine(self, ircClientObject, events): XXX
    def _inputRoutine(self, ircClientObject, events):
        eventsOut, unqueueFlag, paramsOut, status = [], False, None, True
        for event in events:
            if  event["eventType"] == "timer"               \
            and "unqueue" in event:
                for unqueueLine in event["unqueue"]:
                    eventsOut += [{**unqueueLine, "delayed":True}]; unqueueFlag = True;
                continue
            else:
                self._logRoutine(isOutput=False, **event)
                if self.options["debug"]:
                    gameSnapshot = copy.deepcopy(self.typeObjects[ArabolyState])
                    status, newEventsOut, paramsOut = self.unit(event, debug=True)
                else:
                    status, newEventsOut, paramsOut = self.unit(event)
                if self.options["debug"] and not status:
                    with open(self.options["snapshot_path"], "w") as fileObject:
                        print("Saving pre-exception game snapshot to {}!".format(self.options["snapshot_path"]))
                        yaml.dump(gameSnapshot, fileObject)
                        exit(1)
                if  self.options["recording"] and status    \
                and paramsOut["eventType"] == "command"     \
                and paramsOut["status"]:
                    self._inputRecordRoutine(event, paramsOut)
                eventsOut += newEventsOut
        return eventsOut, paramsOut, unqueueFlag, status
    # }}}
    # {{{ _inputRecordRoutine(self, event, paramsOut): XXX
    def _inputRecordRoutine(self, event, paramsOut):
        if paramsOut["cmd"] == "start":
            self.options["recording_path"] = os.path.join("savefiles", "{}@{}_{}.yml".format(   \
                    self.typeObjects[ArabolyState].clientParams["channel"],                     \
                    self.typeObjects[ArabolyState].clientParams["hostname"],                    \
                    datetime.now().strftime("%Y%m%d%H%M%S")))
        if "recording_path" in self.options:
            with open(self.options["recording_path"], "a+") as fileObject:
                if len(self.typeObjects[ArabolyState].clientParams["recordingXxxLastArgs"]) == 0:
                    newItemArgs = paramsOut["args"]
                else:
                    newItemArgs = self.typeObjects[ArabolyState].clientParams["recordingXxxLastArgs"]
                    self.typeObjects[ArabolyState].clientParams["recordingXxxLastArgs"] = []
                newItem = {
                    "args":newItemArgs,
                    "channel":self.typeObjects[ArabolyState].clientParams["channel"],
                    "cmd":paramsOut["cmd"],
                    "src":paramsOut["src"],
                    "srcFull":paramsOut["srcFull"],
                    "time":int(time.time()),
                    "eventType":paramsOut["eventType"]}
                fileObject.write(yaml.dump([newItem]))
            if self.typeObjects[ArabolyState].clientParams["recordingXxxGameEnded"]:
                del self.options["recording_path"]
    # }}}
    # {{{ _logRoutine(self, isOutput, **event): XXX
    def _logRoutine(self, isOutput, **event):
        eventLevel = event["outputLevel"] if "outputLevel" in event else None;
        if event["eventType"] == "timer" \
        or eventLevel == ArabolyOutputLevel.LEVEL_GRAPHICS:
            return
        elif event["eventType"] == "command":
            ts = datetime.now().strftime("%d-%b-%Y %H:%M:%S").upper()
            cmd = event["cmd"]; msg = " ".join(event["args"]).rstrip("\n");
            channel = event["channel"]; msg = ": " + msg if len(msg) else "";
            if isOutput:
                print("{} {} Command {} output {} to {}{}".format(ts, ">>>", cmd, channel, msg))
            else:
                src = event["src"]
                print("{} {} Command {} from {} on {}{}".format(ts, "<<<", cmd, src, channel, msg))
        elif event["eventType"] == "message":
            ts = datetime.now().strftime("%d-%b-%Y %H:%M:%S").upper()
            destType = "channel " + event["args"][0] if event["args"][0][0] == "#" else "server"
            cmdType = event["cmd"].upper() + " command"
            msg = " ".join(event["args"][1:]).rstrip("\n")
            msg = ": " + msg if len(msg) else ""
            if isOutput:
                dest = " to " + event["args"][0] if "args" in event else ""
                print("{} {} {} {}{}{}".format(ts, ">>>", destType.title(), cmdType, dest, msg))
            else:
                src = " from " + event["src"] if "src" in event else ""
                print("{} {} {} {}{}{}".format(ts, "<<<", destType.title(), cmdType, src, msg))
    # }}}
    # {{{ _outputRoutine(self, eventsObject, ircClientObject, events, unqueueFlag): XXX
    def _outputRoutine(self, eventsObject, ircClientObject, events, unqueueFlag):
        floodDelay, queueList = 0, []
        for event in events:
            if event["eventType"] == "message":
                msg = {k:event[k] for k in event if k in ["args", "cmd"]}
                eventLevel = event["outputLevel"] if "outputLevel" in event else None
                if "delayed" in event:
                    self._logRoutine(isOutput=True, **event)
                    queueList, unqueueFlag = queueList + [msg], True
                elif not "delayed" in event:
                    if self.options["flood_delay"] > 0:
                        floodDelay += self.options["flood_delay"]
                        eventsObject.concatTimers(expire=floodDelay, unqueue=[{**msg, "eventType":"message", "delayed":True}])
                    elif eventLevel == ArabolyOutputLevel.LEVEL_GRAPHICS    \
                    or   eventLevel == ArabolyOutputLevel.LEVEL_NODELAY:
                        if floodDelay > 0:
                            eventsObject.concatTimers(expire=floodDelay, unqueue=[{**msg, "eventType":"message", "delayed":True}])
                        else: 
                            self._logRoutine(isOutput=True, **event)
                            queueList, unqueueFlag = queueList + [msg], True
                    elif "delay" in event:
                        floodDelay += event["delay"]
                        eventsObject.concatTimers(expire=floodDelay, unqueue=[{**msg, "eventType":"message", "delayed":True}])
                    elif not "delay" in event:
                        floodDelay += 0.750
                        eventsObject.concatTimers(expire=floodDelay, unqueue=[{**msg, "eventType":"message", "delayed":True}])
            elif event["eventType"] == "timer":
                eventsObject.concatTimers(**event)
        return floodDelay, queueList
    # }}}

    # {{{ synchronise(self): XXX
    def synchronise(self):
        eventsObject = self.typeObjects[ArabolyEvents]
        ircClientObject = self.typeObjects[ArabolyIrcClient]
        status = True
        while status:
            if ircClientObject.connect(self.options["connect_timeout"]):
                clientSocket = ircClientObject.clientSocket.fileno()
                eventsObject.concatSelect(rlist=[clientSocket])
                if ircClientObject.unqueue() != []:
                    eventsObject.concatSelect(wlist=[clientSocket])
                while status:
                    eventsIn, eventsOut, readySet = [], [], eventsObject.select()
                    expiredTimers = eventsObject.timers()
                    if len(readySet[0]) != 0:
                        eventsIn += ircClientObject.readlines()
                    if len(expiredTimers):
                        eventsIn += expiredTimers
                    if len(eventsIn):
                        eventsOut, paramsOut, unqueueFlag, status = self._inputRoutine(ircClientObject, eventsIn)
                        if paramsOut != None:
                            if not status   \
                            or not paramsOut["status"]:
                                eventsOut, status = self._errorRoutine(eventsOut, paramsOut, status)
                    if len(eventsOut):
                        floodDelay, queueList = self._outputRoutine(eventsObject, ircClientObject, eventsOut, unqueueFlag)
                        if len(queueList):
                            for msg in queueList:
                                ircClientObject.queue(**msg)
                            if not ircClientObject.unqueue():
                                eventsObject.concatSelect(wlist=[ircClientObject.clientSocket.fileno()])
                            else:
                                eventsObject.filterSelect(wlist=[ircClientObject.clientSocket.fileno()])
                        if floodDelay > 0:
                            self.typeObjects[ArabolyState].clientParams["inhibitUntil"] = time.time() + floodDelay
                ircClientObject.close()
            else:
                status = False
        return status
    # }}}
    # {{{ __init__(self, argv): initialisation method
    def __init__(self, argv):
        options = {}
        optionsList, args = getopt(argv[1:], self.optionsString)
        for optionChar, optionArg in optionsList:
            optionName = self.optionsStringMap[optionChar[1:]]
            if type(self.optionsDefault[optionName]) == bool:
                options[optionName] = True
            else:
                options[optionName] = optionArg
        if "help" in options or "hostname" not in options:
            if "hostname" not in options:
                print("error: missing hostname\n", file=sys.stderr); rc = 1;
            else:
                rc = 0
            with open(os.path.join("assets", "text", "ArabolyIrcBotUsage.txt"), "r") as fileObject:
                for usageLine in fileObject.readlines():
                    print(usageLine.rstrip("\n"), file=sys.stderr)
            exit(rc)
        if "flood_delay" in options:
            options["flood_delay"] = float(options["flood_delay"]) / 1000.0
        if "ssl" in options and "port" not in options:
            options["port"] = "6697"
        super().__init__(options)
        if "debug" in options:
            self.options["snapshot_path"] = self.optionsDefault["snapshot_path"]
            self.options["snapshot_path"] += "." + self.options["hostname"]
            if os.path.exists(self.options["snapshot_path"]):
                with open(self.options["snapshot_path"], "r") as fileObject:
                    print("Loading game snapshot from {}!".format(self.options["snapshot_path"]))
                    self.typeObjects[ArabolyState] = yaml.load(fileObject)
    # }}}

if __name__ == "__main__":
    exit(ArabolyIrcBot(sys.argv).synchronise())

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=0
