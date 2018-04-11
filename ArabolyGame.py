#!/usr/bin/env python3
#
# Araboly NT 3.1 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from collections import defaultdict
from enum import Enum

nested_dict = lambda: defaultdict(nested_dict)

class ArabolyGameField(Enum):
    """XXX"""
    NONE = 0
    CHANCE = 1
    CHEST = 2
    FREE_LSD = 3
    LOONY_BIN = 4
    PROPERTY = 5
    SECTIONED = 6
    START = 7
    TAX = 8
    UTILITY = 9

class ArabolyPropSubType(Enum):
    """XXX"""
    NONE = 0
    BUY = 1
    HOUSE = 2
    LEVEL = 2
    RENT = 3

class ArabolyGameState(Enum):
    """XXX"""
    DISABLED = 0
    ATTRACT = 1
    SETUP = 2
    GAME = 3
    PROPERTY = 4
    AUCTION = 5

class ArabolyGame(object):
    """XXX"""
    auctionProperty = []; auctionBidders = -1; auctionBids = {};
    clientParams = {}; clientUaf = [];
    playerCur = -1; players = []; playersMax = -1;
    board = []; boardStrings = nested_dict(); boardTmp = [];
    fields = {}; properties = {}; state = ArabolyGameState.ATTRACT; wallets = {};

    #
    # __init__(self, **kwargs): initialisation method
    def __init__(self, **kwargs):
        self.board.clear()
        with open("assets/ArabolyBoard.lst", "r") as fileObject:
            for fileLine in fileObject.readlines():
                fileFields = [f for f in fileLine.rstrip("\n").split("\t") if len(f)]
                if fileFields[0] == "BUY"   \
                or fileFields[0] == "HOUSE" \
                or fileFields[0] == "LEVEL" \
                or fileFields[0] == "RENT":
                    propIdx = len(self.board)-1 if len(self.board) else 0
                    propSubType, levelNum, houseNum, msg = fileFields[0], int(fileFields[1]), int(fileFields[2]), *fileFields[3:]
                    propSubType = getattr(ArabolyPropSubType, propSubType)
                    if houseNum not in self.boardStrings[propIdx][propSubType][levelNum]:
                        self.boardStrings[propIdx][propSubType][levelNum][houseNum] = []
                    self.boardStrings[propIdx][propSubType][levelNum][houseNum] += [msg]
                else:
                    lineType, linePrice, lineColour, lineTitle = fileFields[0], int(fileFields[1]), fileFields[2], *fileFields[3:]
                    lineType = getattr(ArabolyGameField, lineType)
                    self.board += [[lineType, linePrice, lineColour, lineTitle, 1, [-1, 0, 0, 0]]]
        with open("assets/ArabolyBoard.irc", "r") as fileObject:
            self.boardTmp = fileObject.readlines()
        self.clientParams = kwargs.copy()
        self.clientUaf.clear()
        with open("assets/ArabolyIrcBot.uaf", "r") as fileObject:
            for fileLine in fileObject.readlines():
                fileLine = fileLine.rstrip("\n")
                if  not fileLine.startswith("#")    \
                and not len(fileLine) == 0:
                    fileFields = [f for f in fileLine.split("\t") if len(f)]
                    hostnameMask, channelMask, clientMask = fileFields[0], fileFields[1], fileFields[2]
                    self.clientUaf += [[hostnameMask, channelMask, clientMask]]

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120
