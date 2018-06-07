#!/usr/bin/env python3
#
# Araboly 2000 Advanced Server SP1 -- everyone's favourite board game... with IRC support and fancy colours!
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

    # {{{ _land_field(channel, context, output, src, srcField, srcFieldPastGo, srcPlayer): XXX
    @staticmethod
    def _land_field(channel, context, output, src, srcField, srcFieldPastGo, srcPlayer):
        if srcFieldPastGo:
            srcPlayer["wallet"] += 200
            output = ArabolyGenerals._push_output(channel, context, output, "Yay! {src} passes past GO and collects $200!".format(**locals()))
        output = ArabolyGenerals._push_output(channel, context, output, "{src} lands on {srcField[title]}!".format(**locals()))
        if srcField["type"] == ArabolyGameField.PROPERTY    \
        or srcField["type"] == ArabolyGameField.UTILITY:
            context, output, srcField, srcPlayer = ArabolyFields._land_property_utility(channel, context, output, src, srcField, srcPlayer)
        elif srcField["type"] == ArabolyGameField.TAX:
            context, output, srcField, srcPlayer = ArabolyFields._land_tax(channel, context, output, src, srcField, srcPlayer)
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
                    output = ArabolyGenerals._push_output(channel, context, output, rentString.format(cost=srcPropRent, owner=srcField["owner"], prop=srcField["title"], rands=rands, who=src), ArabolyOutputLevel.LEVEL_NODELAY)
                context.players["byName"][srcField["owner"]]["wallet"] += srcPropRent
                srcPlayer["wallet"] -= srcPropRent
        return context, output, srcField, srcPlayer
    # }}}
    # {{{ _land_tax(channel, context, output, src, srcField, srcPlayer): XXX
    @staticmethod
    def _land_tax(channel, context, output, src, srcField, srcPlayer):
        output = ArabolyGenerals._push_output(channel, context, output, "Oh no! {src} must pay ${srcField[price]}!".format(**locals()))
        srcPlayer["wallet"] -= srcField["price"]
        return context, output, srcField, srcPlayer
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=0
