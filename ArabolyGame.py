#!/usr/bin/env python3
#
# Araboly NT 3.1 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

from collections import defaultdict

def nested_dict():
    return defaultdict(nested_dict)

ArabolyColourMiRCMap = defaultdict(int, {
    "BLUE":12,
    "DARK_BLUE":2,
    "DARK_GREEN":3,
    "DARK_RED":5,
    "GREEN":9,
    "PINK":13,
    "RED":4,
    "YELLOW":8,
})

class ArabolyGameField():
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

class ArabolyPropSubType():
    """XXX"""
    NONE = 0
    BUY = 1
    HOUSE = 2
    LEVEL = 2
    RENT = 3

class ArabolyGameState():
    """XXX"""
    DISABLED = 0
    ATTRACT = 1
    SETUP = 2
    GAME = 3
    PROPERTY = 4
    AUCTION = 5

class ArabolyGame(object):
    """XXX"""

    #
    # __init__(self, **kwargs): initialisation method
    def __init__(self, **kwargs):
        self.auctionBids = {}; self.auctionProperty = {};
        self.clientParams = {}; self.clientUaf = [];
        self.playerCur = -1; self.players = []; self.playersMax = -1; self.tradeDict = {};
        self.board = []; self.boardStrings = nested_dict();
        self.fields = {}; self.properties = {}; self.state = ArabolyGameState.ATTRACT; self.wallets = {};
        self.inhibitUntil = 0
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
                    lineType = getattr(ArabolyGameField, fileFields[0])
                    self.board += [{"type":lineType, "price":int(fileFields[1]), "colour":fileFields[2], "colourMiRC":ArabolyColourMiRCMap[fileFields[2]], "mortgaged":False, "title":fileFields[3], "level":1, "houses":[-1, 0, 0, 0]}]
        self.boardFields = {}
        with open("assets/ArabolyBoardField25.irc", "r") as fileObject:
            self.boardFields[25] = fileObject.readlines()
        with open("assets/ArabolyBoardSouth.irc", "r") as fileObject:
            self.boardSouth = fileObject.readlines()
        with open("assets/ArabolyBoardWest.irc", "r") as fileObject:
            self.boardWest = fileObject.readlines()
        with open("assets/ArabolyBoardNorth.irc", "r") as fileObject:
            self.boardNorth = fileObject.readlines()
        with open("assets/ArabolyBoardNorthEast.irc", "r") as fileObject:
            self.boardNorthEast = fileObject.readlines()
        with open("assets/ArabolyBoardSouthEast.irc", "r") as fileObject:
            self.boardSouthEast = fileObject.readlines()
        with open("assets/ArabolyAttract.irc", "r") as fileObject:
            self.attractLinesList = "".join(fileObject.readlines()).split("\n")
            self.attractLinesList = [x[:-1].split("\n") for x in self.attractLinesList]
        with open("assets/ArabolyLogo.irc", "r") as fileObject:
            self.logoLines = fileObject.readlines()
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
