#!/usr/bin/env python3
#
# Araboly 2000 Advanced Server SP3 -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from ArabolyRtl import ArabolyDefaultDict, ArabolyGlob, ArabolyNestedDict
import yaml, os

ArabolyColourMiRCMap = ArabolyDefaultDict(int, {
    "NONE":-1, "BLUE":12, "DARK_BLUE":2, "DARK_GREEN":3, "DARK_RED":5, "GREEN":9, "PINK":13, "RED":4, "YELLOW":8})
class ArabolyGameField(object):
    CHANCE = 1; CHEST = 2; FREE_LSD = 3; LOONY_BIN = 4; PROPERTY = 5; SECTIONED = 6; START = 7; TAX = 8; UTILITY = 9; CHRONO = 10;
class ArabolyGameState(object):
    DISABLED = 0; ATTRACT = 1; SETUP = 2; GAME = 3; PROPERTY = 4; AUCTION = 5; BANKRUPTCY = 6
class ArabolyOutputLevel():
    LEVEL_GRAPHICS = 1; LEVEL_NODELAY = 2;
class ArabolyStringType(object):
    DEVELOP = 1; LAND = 2; NAME = 3; RENT = 4

class ArabolyState(object):
    """XXX"""
    initDictsClear = ["auctionState", "board", "clientParams", "graphics", "kades", "players", "tradeState"]
    initFunctions = ["board", "clientParams", "graphics", "kades"]
    initVariables = {                                           \
        "auctionState":{"bids":{}, "field":None, "minBid":-1},  \
        "players":{"byName":{}, "curNum":-1, "numMap":[]},      \
        "state":ArabolyGameState.ATTRACT}

    # {{{ _initBoard(self, boardPathName=os.path.join("assets", "YAML", "ArabolyBoard.yml"), fieldsDirName=os.path.join("assets", "MiRCart"), fieldsPatterns=["ArabolyBoardFields([0-9][0-9])_([0-9][0-9]).irc", "ArabolyBoardField([0-9][0-9]?).irc"], **kwargs):
    def _initBoard(self, boardPathName=os.path.join("assets", "YAML", "ArabolyBoard.yml"), fieldsDirName=os.path.join("assets", "MiRCart"), fieldsPatterns=["ArabolyBoardFields([0-9][0-9])_([0-9][0-9]).irc", "ArabolyBoardField([0-9][0-9]?).irc"], **kwargs):
        with open(boardPathName, "r") as fileObject:
            self.board = yaml.load(fileObject)
        self.graphics["fields"] = []
        for fileInfo in ArabolyGlob(fieldsDirName, fieldsPatterns):
            if len(fileInfo["matches"]) == 1:
                fieldMin, fieldMax = [int(fileInfo["matches"][0])] * 2
            elif len(fileInfo["matches"]) == 2:
                fieldMin, fieldMax = [int(m) for m in fileInfo["matches"]]
            with open(fileInfo["pathName"], "r") as fileObject:
                self.graphics["fields"] += [[fieldMin, fieldMax, fileObject.readlines()]]
    # }}}
    # {{{ _initClientParams(self, channel, debug=False, hostname=None, recording=False, testing=False, uafPathName=os.path.join("assets", "YAML", "ArabolyIrcBotUaf.yml"), **kwargs): XXX
    def _initClientParams(self, channel, debug=False, hostname=None, recording=False, testing=False, uafPathName=os.path.join("assets", "YAML", "ArabolyIrcBotUaf.yml"), **kwargs):
        self.clientParams["channel"] = channel
        self.clientParams["channelRejoin"] = False
        self.clientParams["debug"] = debug
        self.clientParams["hostname"] = hostname
        self.clientParams["nickMap"] = {}
        self.clientParams["recording"] = recording
        if recording:
            self.clientParams["recording_path"] = ""
            self.clientParams["recordingXxxGameEnded"] = False
            self.clientParams["recordingXxxLastArgs"] = []
        self.clientParams["testing"] = testing
        self.clientParams["inhibitUntil"] = 0; self.clientParams.update(kwargs);
        with open(uafPathName, "r") as fileObject:
            self.clientParams["uaf"] = yaml.load(fileObject)
    # }}}
    # {{{ _initGraphics(self, dirName=os.path.join("assets", "MiRCart"), **kwargs): XXX
    def _initGraphics(self, dirName=os.path.join("assets", "MiRCart"), **kwargs):
        with open(os.path.join(dirName, "ArabolyAttract.irc"), "r") as fileObject:
            self.graphics["attract"] = "".join(fileObject.readlines()).split("\n")
            self.graphics["attract"] = [x[:-1].split("\n") for x in self.graphics["attract"]]
        with open(os.path.join(dirName, "ArabolyIrcBot.hlp"), "r") as fileObject:
            self.graphics["help"] = fileObject.readlines()
        with open(os.path.join(dirName, "ArabolyLogo.irc"), "r") as fileObject:
            self.graphics["logo"] = fileObject.readlines()
        with open(os.path.join(dirName, "explosion.irc"), "r") as fileObject:
            self.graphics["explosion"] = fileObject.readlines()
    # }}}
    # {{{ _initKades(self, kadesDirName=os.path.join("assets", "kades"), kadesPatterns=["kade([0-9]+)\.irc"], **kwargs):
    def _initKades(self, kadesDirName=os.path.join("assets", "kades"), kadesPatterns=["kade([0-9]+)\.irc"], **kwargs):
        for fileInfo in ArabolyGlob(kadesDirName, kadesPatterns):
            kadeIdx = fileInfo["matches"][0]
            with open(fileInfo["pathName"], "r") as fileObject:
                self.kades[int(kadeIdx)] = fileObject.readlines()
    # }}}
    # {{{ __init__(self, **kwargs): initialisation method
    def __init__(self, **kwargs):
        for initDictName in self.initDictsClear:
            setattr(self, initDictName, {})
        for initFunName in self.initFunctions:
            initFunName = "_init" + initFunName[0].upper() + initFunName[1:]
            getattr(self, initFunName)(**kwargs)
        for initVarName, initVarVal in self.initVariables.items():
            if type(initVarVal) == dict:
                getattr(self, initVarName).update(initVarVal)
            else:
                setattr(self, initVarName, initVarVal)
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=0
