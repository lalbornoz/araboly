#!/usr/bin/env python3
#
# Araboly NT 3.1 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

class ArabolyTypeClass(object):
    """XXX"""

    # {{{ dispatch_bid(self, context, eventsOut, status, cmd, player, channel, price=None, *args): XXX
    def dispatch_bid(self, context, eventsOut, status, cmd, player, channel, price=None, *args):
        raise TypeError
    # }}}
    # {{{ dispatch_board(self, context, eventsOut, status, cmd, player, channel, *args): XXX
    def dispatch_board(self, context, eventsOut, status, cmd, player, channel, *args):
        raise TypeError
    # }}}
    # {{{ dispatch_buy(self, context, eventsOut, status, cmd, player, channel, *args): XXX
    def dispatch_buy(self, context, eventsOut, status, cmd, player, channel, *args):
        raise TypeError
    # }}}
    # {{{ dispatch_cheat(self, context, eventsOut, status, cmd, player, channel, *args): XXX
    def dispatch_cheat(self, context, eventsOut, status, cmd, player, channel, *args):
        raise TypeError
    # }}}
    # {{{ dispatch_develop(self, context, eventsOut, status, cmd, player, channel, field=None, level=None, *args): XXX
    def dispatch_develop(self, context, eventsOut, status, cmd, player, channel, field=None, level=None, *args):
        raise TypeError
    # }}}
    # {{{ dispatch_dice(self, context, eventsOut, status, cmd, player, channel, *args): XXX
    def dispatch_dice(self, context, eventsOut, status, cmd, player, channel, *args):
        raise TypeError
    # }}}
    # {{{ dispatch_help(self, context, eventsOut, status, cmd, player, channel, *args): XXX
    def dispatch_help(self, context, eventsOut, status, cmd, player, channel, *args):
        raise TypeError
    # }}}
    # {{{ dispatch_join(self, context, eventsOut, status, cmd, player, channel, *args): XXX
    def dispatch_join(self, context, eventsOut, status, cmd, player, channel, *args):
        raise TypeError
    # }}}
    # {{{ dispatch_kick(self, context, eventsOut, status, cmd, player, channel, otherPlayer=None, *args): XXX
    def dispatch_kick(self, context, eventsOut, status, cmd, player, channel, otherPlayer=None, *args):
        raise TypeError
    # }}}
    # {{{ dispatch_part(self, context, eventsOut, status, cmd, player, channel, *args): XXX
    def dispatch_part(self, context, eventsOut, status, cmd, player, channel, *args):
        raise TypeError
    # }}}
    # {{{ dispatch_pass(self, context, eventsOut, status, cmd, player, channel, *args): XXX
    def dispatch_pass(self, context, eventsOut, status, cmd, player, channel, *args):
        raise TypeError
    # }}}
    # {{{ dispatch_start(self, context, eventsOut, status, cmd, player, channel, players=None, *args): XXX
    def dispatch_start(self, context, eventsOut, status, cmd, player, channel, players=None, *args):
        raise TypeError
    # }}}
    # {{{ dispatch_status(self, context, eventsOut, status, cmd, player, channel, *args): XXX
    def dispatch_status(self, context, eventsOut, status, cmd, player, channel, *args):
        raise TypeError
    # }}}
    # {{{ dispatch_stop(self, context, eventsOut, status, cmd, player, channel, *args): XXX
    def dispatch_stop(self, context, eventsOut, status, cmd, player, channel, *args):
        raise TypeError
    # }}}
    # {{{ __init__(self, **kwargs): initialisation method
    def __init__(self, **kwargs):
        pass
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120
