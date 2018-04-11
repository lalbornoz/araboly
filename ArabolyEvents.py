#!/usr/bin/env python3
#
# Araboly NT 3.1 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

import select

class ArabolyEvents(object):
    """XXX"""
    nextTimeout = None; timers = [];
    rlist = []; wlist = []; xlist = [];

    # {{{ concatSelect(self, rlist=[], wlist=[], xlist=[]): XXX
    def concatSelect(self, rlist=[], wlist=[], xlist=[]):
        self.rlist += rlist; self.wlist += wlist; self.xlist += xlist;
    # }}}
    # {{{ concatTimers(self, timers): XXX
    def concatTimers(self, timers):
        self.timers = sorted(self.timers + [{"type":"timer", **timers}], key="expire")
        if len(self.timers):
            self.nextTimeout = self.timers[0]["expire"]
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
        self.timers = [timer for timer in self.timers if timer not in timers]
        if len(self.timers):
            self.timers = sorted(self.timers)
            self.nextTimeout = self.timers[0][0]
        else:
            self.nextTimeout = None
    # }}}
    # {{{ select(self): XXX
    def select(self):
        if self.nextTimeout:
            timeNow = time.time()
            readySet = select.select(self.rlist, self.wlist, self.xlist, nextTimeout - timeNow)
        else:
            readySet = select.select(self.rlist, self.wlist, self.xlist)
        return readySet
    # }}}
    # {{{ timers(self): XXX
    def timers(self):
        timers = []
        if self.nextTimeout:
            timeNow = time.time()
            for timerIdx in range(len(self.timers)):
                if self.timers[timerIdx]["expire"] <= timeNow:
                    timers += self.timers[timerIdx].copy()
                    del self.timers[timerIdx]
                    if len(self.timers):
                        self.nextTimeout = self.timers[0]["expire"]
                    else:
                        self.nextTimeout = None
        return timers
    # }}}
    # {{{ __init__(self, **kwargs): initialisation method
    def __init__(self, **kwargs):
        pass
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120
