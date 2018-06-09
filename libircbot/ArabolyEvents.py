#!/usr/bin/env python3
#
# Araboly 2000 Advanced Server SP2 -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from select import select
from time import time

class ArabolyEvents(object):
    """XXX"""

    # {{{ concatSelect(self, rlist=[], wlist=[], xlist=[]): XXX
    def concatSelect(self, rlist=[], wlist=[], xlist=[]):
        self.rlist += rlist; self.wlist += wlist; self.xlist += xlist;
    # }}}
    # {{{ concatTimers(self, **timer): XXX
    def concatTimers(self, **timer):
        timer_ = timer.copy(); timer_["expire"] += time();
        self.timerList = sorted(self.timerList + [{"eventType":"timer", **timer_}], key=lambda x: x["expire"])
        if len(self.timerList):
            self.nextTimeout = self.timerList[0]["expire"]
        else:
            self.nextTimeout = None
    # }}}
    # {{{ filterSelect(self, rlist=[], wlist=[], xlist=[]): XXX
    def filterSelect(self, rlist=[], wlist=[], xlist=[]):
        self.rlist = [r for r in self.rlist if r not in rlist]
        self.wlist = [w for w in self.wlist if w not in wlist]
        self.xlist = [x for x in self.xlist if x not in xlist]
    # }}}
    # {{{ filterTimers(self, timers): XXX
    def filterTimers(self, timers):
        self.timerList = [timer for timer in self.timerList if timer not in timers]
        if len(self.timerList):
            self.timerList = sorted(self.timerList)
            self.nextTimeout = self.timerList[0]["expire"]
        else:
            self.nextTimeout = None
    # }}}
    # {{{ select(self): XXX
    def select(self):
        timeNow = time()
        if self.nextTimeout:
            if self.nextTimeout > timeNow:
                readySet = select(self.rlist, self.wlist, self.xlist, self.nextTimeout - timeNow)
            else:
                readySet = select(self.rlist, self.wlist, self.xlist, 0)
        else:
            readySet = select(self.rlist, self.wlist, self.xlist)
        return readySet
    # }}}
    # {{{ timers(self): XXX
    def timers(self):
        timers = []
        if self.nextTimeout:
            timeNow = time()
            for timerIdx in range(len(self.timerList)):
                if self.timerList[timerIdx]["expire"] <= timeNow:
                    timers += [self.timerList[timerIdx].copy()]
                    self.timerList[timerIdx]["_delete"] = True
            self.timerList = [a for a in self.timerList if "_delete" not in a]
            if len(self.timerList):
                self.nextTimeout = self.timerList[0]["expire"]
            else:
                self.nextTimeout = None
        return timers
    # }}}
    # {{{ __init__(self, **kwargs): initialisation method
    def __init__(self, **kwargs):
        self.nextTimeout = None; self.timerList = [];
        self.rlist = []; self.wlist = []; self.xlist = [];
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=0
