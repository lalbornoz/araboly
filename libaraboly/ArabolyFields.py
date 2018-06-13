#!/usr/bin/env python3
#
# Araboly 2000 Advanced Server SP2 -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#
# List of ideas:
# {{{
# 1)  Araboly field: random chance of (fake) game crash for <n> turns w/ decay; Windows 10 field; mosque field; narration of khalawayh
# 2)  Chance: randomly chosen from {{Chrono,Community} *,Free LSD,{Gaol,Loony bin},Tax} fields
# 3)  Chrono *: allow a player to swap places with another placers piece
# 4)  Chrono *: allow travel for fee w/ chance of random travel
# 5)  Community brr: split into Community {asshurt,brr,opal,rachel}, player control as premise
# 6)  Community *: allow control over taxes for <n> turns, vary tax types
# 7)  Community *: cards from <http://monopoly.wikia.com/wiki/Community_Chest>
# 8)  Community *: rob another player
# 9)  Community *: start curse (mortgage something) of the <n>th player mode for <n> turns
# 10) Community *: start slumlord mode for <n> turns
# 11) Community *: turn another players currency into 100 VXP == 100 ODB == 100 RZA == 100 GZA (+ BTC, ETH, ...)
# 12) Free LSD: board {graphics,strings} filters
# 13) Free LSD: Drug addictions
# 14) Free LSD: embed efukts ascii/ghost of araboly/spoders
# 15) Free LSD: enter for rand(range(1, 10)) turns w/ random decay
# 16) Free LSD: randomly refuse to work & blog botquote/kadequote/...
# 17) {Gaol,Loony bin}: enter on rolling doubles
# 18) {Gaol,Loony bin}: stay for <n> turns
# 19) {Gaol,Loony bin}: visit {acid,npk} in gaol/visit ? in loony bin
# 20) IRC housing projects: don't collect rent at random, squatting
# 22) Utility fields: write strings
# }}}
#

from ArabolyGenerals import ArabolyGenerals
from ArabolyMonad import ArabolyDecorator
from ArabolyPropertyMode import ArabolyPropertyMode
from ArabolyRtl import ArabolyRandom
from ArabolyState import ArabolyGameField, ArabolyOutputLevel, ArabolyStringType
from ArabolyTypeClass import ArabolyTypeClass

@ArabolyDecorator()
class ArabolyFields(ArabolyTypeClass):
    """XXX"""

    # {{{ _land_field(args, channel, context, output, src, srcField, srcFieldPastGo, srcFull, srcPlayer, status): XXX
    @staticmethod
    def _land_field(args, channel, context, output, src, srcField, srcFieldPastGo, srcFull, srcPlayer, status):
        if srcFieldPastGo:
            srcPlayer["wallet"] += 200
            output = ArabolyGenerals._push_output(channel, context, output, "Yay! {src} passes past GO and collects $200!".format(**locals()))
        output = ArabolyGenerals._push_output(channel, context, output, "{src} lands on {srcField[title]}!".format(**locals()))
        if srcField["type"] == ArabolyGameField.CHANCE:
            context, output, srcField, srcPlayer, status = ArabolyFields._land_chance(args, channel, context, output, src, srcField, srcFull, srcPlayer, status)
        elif srcField["type"] == ArabolyGameField.CHEST:
            context, output, srcField, srcPlayer = ArabolyFields._land_chest(channel, context, output, src, srcField, srcPlayer)
        elif srcField["type"] == ArabolyGameField.CHRONO:
            context, output, srcField, srcPlayer = ArabolyFields._land_chrono(channel, context, output, src, srcField, srcPlayer)
        elif srcField["type"] == ArabolyGameField.FREE_LSD:
            context, output, srcField, srcPlayer = ArabolyFields._land_free_lsd(channel, context, output, src, srcField, srcPlayer)
        elif srcField["type"] == ArabolyGameField.LOONY_BIN:
            context, output, srcField, srcPlayer = ArabolyFields._land_loony_bin(channel, context, output, src, srcField, srcPlayer)
        elif srcField["type"] == ArabolyGameField.PROPERTY  \
        or   srcField["type"] == ArabolyGameField.UTILITY:
            context, output, srcField, srcPlayer = ArabolyFields._land_property_utility(channel, context, output, src, srcField, srcPlayer)
        elif srcField["type"] == ArabolyGameField.SECTIONED:
            context, output, srcField, srcPlayer = ArabolyFields._land_sectioned(channel, context, output, src, srcField, srcPlayer)
        elif srcField["type"] == ArabolyGameField.TAX:
            context, output, srcField, srcPlayer = ArabolyFields._land_tax(channel, context, output, src, srcField, srcPlayer)
        return context, output, srcField, srcPlayer, status
    # }}}

    # {{{ _land_chance(args, channel, context, output, src, srcField, srcFull, srcPlayer, status): XXX
    @staticmethod
    def _land_chance(args, channel, context, output, src, srcField, srcFull, srcPlayer, status):
        if len(args):
            if ArabolyGenerals._authorised(channel, context, srcFull)   \
            or context.clientParams["testing"]:
                randsFromArgs = True
            else:
                status = False
                return context, output, srcField, srcPlayer, status
        else:
            randsFromArgs = False
        for kadeLine in context.kades[ArabolyRandom(limit=len(context.kades))]:
            output = ArabolyGenerals._push_output(channel, context, output, kadeLine.rstrip("\n"), outputLevel=ArabolyOutputLevel.LEVEL_GRAPHICS)
        output = ArabolyGenerals._push_output(channel, context, output, "Kade thinks!", delay=1)
        output = ArabolyGenerals._push_output(channel, context, output, "Kade is thinking!", delay=2)
        srcPlayer = context.players["byName"][src]
        kadecision = ArabolyRandom(max=5, min=1) if not randsFromArgs else int(args[0])
        if context.clientParams["recording"]:
            context.clientParams["recordingXxxLastArgs"] = [kadecision]
        if kadecision == 1:
            context, output, srcPlayer = ArabolyFields._land_chance_bank(args, channel, context, output, randsFromArgs, src, srcPlayer)
        elif kadecision == 2:
            context, output, srcPlayer = ArabolyFields._land_chance_mortgage(args, channel, context, output, randsFromArgs, src, srcPlayer)
        elif kadecision == 3:
            context, output, srcPlayer = ArabolyFields._land_chance_swap(args, channel, context, output, randsFromArgs, src, srcPlayer)
        elif kadecision == 4:
            context, output, srcPlayer = ArabolyFields._land_chance_redist(args, channel, context, output, randsFromArgs, src, srcPlayer)
        else:
            output = ArabolyGenerals._push_output(channel, context, output, "Hm! Kade feels stupid!", delay=3)
        return context, output, srcField, srcPlayer, status
    # }}}
    # {{{ _land_chance_bank(args, channel, context, output, randsFromArgs, src, srcPlayer): XXX
    @staticmethod
    def _land_chance_bank(args, channel, context, output, randsFromArgs, src, srcPlayer):
        if not randsFromArgs:
            srcWealth = ArabolyRandom(limit=int(srcPlayer["wallet"] * 0.15), min=int(srcPlayer["wallet"] * 0.05))
            if context.clientParams["recording"]:
                context.clientParams["recordingXxxLastArgs"] += [srcWealth]
        else:
            srcWealth = int(args[1])
        srcPlayer["wallet"] -= srcWealth
        output = ArabolyGenerals._push_output(channel, context, output, "Oh no! Kade gives ${srcWealth} of {src}'s wealth to the bank!".format(**locals()), delay=3)
        return context, output, srcPlayer
    # }}}
    # {{{ _land_chance_mortgage(args, channel, context, output, randsFromArgs, src, srcPlayer): XXX
    @staticmethod
    def _land_chance_mortgage(args, channel, context, output, randsFromArgs, src, srcPlayer):
        if len(srcPlayer["properties"]):
            if not randsFromArgs:
                srcPropNum = ArabolyRandom(limit=len(srcPlayer["properties"]))
                if context.clientParams["recording"]:
                    context.clientParams["recordingXxxLastArgs"] += [srcPropNum]
            else:
                srcPropNum = int(args[1])
            srcProp = context.board[srcPlayer["properties"][srcPropNum]]
            if srcProp["mortgaged"]:
                srcProp["mortgaged"] = False
                output = ArabolyGenerals._push_output(channel, context, output, "Yay! Kade accidentally lifts the mortgage on {src}'s {srcProp[title]}!".format(**locals()), delay=3)
            else:
                srcProp["mortgaged"] = True
                output = ArabolyGenerals._push_output(channel, context, output, "Oh dear! Kade accidentally mortgages {src}'s {srcProp[title]}!".format(**locals()), delay=3)
        else:
            output = ArabolyGenerals._push_output(channel, context, output, "Hm! Kade feels stupid!", delay=3)
        return context, output, srcPlayer
    # }}}
    # {{{ _land_chance_redist(args, channel, context, output, randsFromArgs, src, srcPlayer): XXX
    @staticmethod
    def _land_chance_redist(args, channel, context, output, randsFromArgs, src, srcPlayer):
        targetPlayer = [p for p in context.players["byName"].keys() if p != src]
        if not randsFromArgs:
            srcWealth = ArabolyRandom(limit=int(srcPlayer["wallet"] * 0.15), min=int(srcPlayer["wallet"] * 0.05))
            targetPlayerNum = ArabolyRandom(limit=len(targetPlayer))
            if context.clientParams["recording"]:
                context.clientParams["recordingXxxLastArgs"] += [srcWealth, targetPlayerNum]
        else:
            srcWealth, targetPlayerNum = int(args[1]), int(args[2])
        targetPlayer = context.players["byName"][targetPlayer[targetPlayerNum]]
        srcPlayer["wallet"] -= srcWealth; targetPlayer["wallet"] += srcWealth;
        output = ArabolyGenerals._push_output(channel, context, output, "Oh my! Kade redistributes ${srcWealth} of {src}'s wealth to {targetPlayer[name]}!".format(**locals()), delay=3)
        return context, output, srcPlayer
    # }}}
    # {{{ _land_chance_swap(args, channel, context, output, randsFromArgs, src, srcPlayer): XXX
    @staticmethod
    def _land_chance_swap(args, channel, context, output, randsFromArgs, src, srcPlayer):
        targetPlayer = [p for p in context.players["byName"].keys() if p != src]
        if not randsFromArgs:
            targetPlayerNum = ArabolyRandom(limit=len(targetPlayer))
            if context.clientParams["recording"]:
                context.clientParams["recordingXxxLastArgs"] += [targetPlayerNum]
        else:
            targetPlayerNum = int(args[1])
        targetPlayer = context.players["byName"][targetPlayer[targetPlayerNum]]
        srcPlayer["field"], targetPlayer["field"] = targetPlayer["field"], srcPlayer["field"]
        output = ArabolyGenerals._push_output(channel, context, output, "Oops! Kade swaps {src} with {targetPlayer[name]}!".format(**locals()), delay=3)
        return context, output, srcPlayer
    # }}}

    # {{{ _land_chest(channel, context, output, src, srcField, srcPlayer): XXX
    @staticmethod
    def _land_chest(channel, context, output, src, srcField, srcPlayer):
        for kadeLine in context.kades[ArabolyRandom(limit=len(context.kades))]:
            output = ArabolyGenerals._push_output(channel, context, output, kadeLine.rstrip("\n"), outputLevel=ArabolyOutputLevel.LEVEL_GRAPHICS)
        return context, output, srcField, srcPlayer
    # }}}
    # {{{ _land_chrono(channel, context, output, src, srcField, srcPlayer): XXX
    @staticmethod
    def _land_chrono(channel, context, output, src, srcField, srcPlayer):
        if srcField["owner"] == -1:
            context, output = ArabolyPropertyMode._enter(channel, context, output, src, srcField, srcPlayer)
        elif srcField["owner"] != -1    \
        and  srcField["owner"] != src:
            if srcField["mortgaged"]:
                output = ArabolyGenerals._push_output(channel, context, output, "Oops! {srcField[owner]} cannot collect rent on {srcField[title]} as it is mortgaged!".format(**locals()))
            else:
                otherChronos = 0
                for srcPropNum in context.players["byName"][srcField["owner"]]["properties"]:
                    srcProp = context.board[srcPropNum]
                    if srcProp["type"] == ArabolyGameField.CHRONO:
                        otherChronos += 1
                srcPropRent = srcField["strings"][ArabolyStringType.RENT][otherChronos][0]
                if srcField["level"] == 1:
                    srcPropRent *= 2
                for rentString in srcField["strings"][ArabolyStringType.LAND][srcField["level"]]:
                    rands = [ArabolyRandom(limit=150-5, min=5) for x in range(10)]
                    output = ArabolyGenerals._push_output(channel, context, output, rentString.format(cost=srcPropRent, owner=srcField["owner"], prop=srcField["title"], rands=rands, who=src))
                context.players["byName"][srcField["owner"]]["wallet"] += srcPropRent
                srcPlayer["wallet"] -= srcPropRent
        return context, output, srcField, srcPlayer
    # }}}
    # {{{ _land_free_lsd(channel, context, output, src, srcField, srcPlayer): XXX
    @staticmethod
    def _land_free_lsd(channel, context, output, src, srcField, srcPlayer):
        for kadeLine in context.kades[ArabolyRandom(limit=len(context.kades))]:
            output = ArabolyGenerals._push_output(channel, context, output, kadeLine.rstrip("\n"), outputLevel=ArabolyOutputLevel.LEVEL_GRAPHICS)
        srcPlayer = context.players["byName"][src]
        if not "hie" in srcPlayer:
            hieAmount = ArabolyRandom(limit=8000, min=200)
            output = ArabolyGenerals._push_output(channel, context, output, "Yay! Kade gives {src} {hieAmount}ug LSD!".format(**locals()), delay=1)
            output = ArabolyGenerals._push_output(channel, context, output, "Awfom! {src} is tripping balls!".format(**locals()), delay=1.5)
            output = ArabolyGenerals._push_output(channel, context, output, "{src} looks at the board!".format(**locals()), delay=2)
            srcPlayer["hie"] = True
            output = ArabolyGenerals._board(channel, context, output, src)
        elif "hie" in srcPlayer:
            output = ArabolyGenerals._push_output(channel, context, output, "Oh no! Kade takes away {src}'s LSD trip!".format(**locals()), delay=1)
            output = ArabolyGenerals._push_output(channel, context, output, "Oops! {src} is no longer hie!".format(**locals()), delay=1.5)
            del srcPlayer["hie"]
        return context, output, srcField, srcPlayer
    # }}}
    # {{{ _land_loony_bin(channel, context, output, src, srcField, srcPlayer): XXX
    @staticmethod
    def _land_loony_bin(channel, context, output, src, srcField, srcPlayer):
        loonyBinPlayers = []
        for otherPlayerName, otherPlayer in context.players["byName"].items():
            if context.board[otherPlayer["field"]]["type"] == ArabolyGameField.LOONY_BIN:
                loonyBinPlayers += [otherPlayerName]
        if len(loonyBinPlayers):
            output = ArabolyGenerals._push_output(channel, context, output, "{} visits {} at the loony bin!".format(src, ", ".join(loonyBinPlayers)))
        else:
            output = ArabolyGenerals._push_output(channel, context, output, "{src} visits the loony bin!".format(**locals()))
        return context, output, srcField, srcPlayer
    # }}}
    # {{{ _land_property_utility(channel, context, output, src, srcField, srcPlayer): XXX
    @staticmethod
    def _land_property_utility(channel, context, output, src, srcField, srcPlayer):
        if srcField["owner"] == -1:
            context, output = ArabolyPropertyMode._enter(channel, context, output, src, srcField, srcPlayer)
        elif srcField["owner"] != -1        \
        and  srcField["owner"] != src:
            if srcField["mortgaged"]:
                output = ArabolyGenerals._push_output(channel, context, output, "Oops! {srcField[owner]} cannot collect rent on {srcField[title]} as it is mortgaged!".format(**locals()))
            else:
                srcPropRent = srcField["strings"][ArabolyStringType.RENT][srcField["level"]][0]
                if  srcField["level"] == 0  \
                and srcField["ownerHasGroup"]:
                    srcPropRent *= 2
                for rentString in srcField["strings"][ArabolyStringType.LAND][srcField["level"]]:
                    rands = [ArabolyRandom(limit=150-5, min=5) for x in range(10)]
                    output = ArabolyGenerals._push_output(channel, context, output, rentString.format(cost=srcPropRent, owner=srcField["owner"], prop=srcField["title"], rands=rands, who=src))
                context.players["byName"][srcField["owner"]]["wallet"] += srcPropRent
                srcPlayer["wallet"] -= srcPropRent
        return context, output, srcField, srcPlayer
    # }}}
    # {{{ _land_sectioned(channel, context, output, src, srcField, srcPlayer): XXX
    @staticmethod
    def _land_sectioned(channel, context, output, src, srcField, srcPlayer):
        for kadeLine in context.kades[ArabolyRandom(limit=len(context.kades))]:
            output = ArabolyGenerals._push_output(channel, context, output, kadeLine.rstrip("\n"), outputLevel=ArabolyOutputLevel.LEVEL_GRAPHICS)
        illnessPrefix = ["acute ", "latent ", "therapy-resistant ", "undifferentiated ", ""][ArabolyRandom(limit=5)]
        illnessTherapy = ["Antipsychotics Treatment", "Cat Room Therapy", "Electroconvulsive Therapy"][ArabolyRandom(limit=3)]
        illnessType = ["Bipolar", "Clinical Depression", "Lethally Severe Autism", "OCPD", "Schizophrenia"][ArabolyRandom(limit=5)]
        output = ArabolyGenerals._push_output(channel, context, output, "Dr Kade thinks!", delay=1)
        output = ArabolyGenerals._push_output(channel, context, output, "Oh dear! Dr Kade diagnoses {src} with {illnessPrefix}{illnessType} and recommends immediate {illnessTherapy}!".format(**locals()), delay=2)
        output = ArabolyGenerals._push_output(channel, context, output, "Oh no! {src} is confined to the loony bin until having rolled doubles!".format(**locals()), delay=3)
        srcPlayer["loonyBinTurns"] = 0
        return ArabolyFields._land_loony_bin(channel, context, output, src, srcField, srcPlayer)
    # }}}
    # {{{ _land_tax(channel, context, output, src, srcField, srcPlayer): XXX
    @staticmethod
    def _land_tax(channel, context, output, src, srcField, srcPlayer):
        output = ArabolyGenerals._push_output(channel, context, output, "Oh no! {src} must pay ${srcField[price]}!".format(**locals()))
        srcPlayer["wallet"] -= srcField["price"]
        return context, output, srcField, srcPlayer
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=0
