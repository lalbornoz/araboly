#!/usr/bin/env python3
#
# Araboly NT 3.1 Advanced Server -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

import select, socket

class ArabolyIrcClient(object):
    """Non-blocking abstraction over the IRC protocol"""
    serverHname = serverPort = None;
    clientNick = clientIdent = clientGecos = None;
    clientSocket = clientSocketFile = None;
    clientQueue = None
    partialLine = ""

    # {{{ close(self): Close connection to server
    def close(self):
        if self.clientSocket != None:
            self.clientSocket.close()
        self.clientSocket = self.clientSocketFile = None;
    # }}}
    # {{{ connect(self, timeout=None): Connect to server and register w/ optional timeout
    def connect(self, timeout=None):
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientSocket.setblocking(0)
        try:
            self.clientSocket.connect((self.serverHname, int(self.serverPort)))
        except BlockingIOError:
            pass
        if timeout:
            readySet = select.select([], [self.clientSocket.fileno()], [], timeout)
            if len(readySet[1]) == 0:
                self.close(); return False;
        else:
            select.select([], [self.clientSocket.fileno()], [])
        self.clientSocketFile = self.clientSocket.makefile(encoding="utf-8", errors="replace")
        self.clientQueue = []
        self.queue("NICK", self.clientNick)
        self.queue("USER", self.clientIdent, "0", "0", self.clientGecos)
        return True
    # }}}
    # {{{ readlines(self): Read and parse lines from server into list of canonicalised lists
    def readlines(self):
        lines = []
        while True:
            msg = self.clientSocketFile.readline()
            if msg == None:
                lines += [None]; break;
            elif len(msg) == 0:
                break
            elif msg[-1] != "\n":
                self.partialLine = msg; break
            else:
                msg = self.partialLine + msg.rstrip("\n")
                self.partialLine = ""
                msg = msg.split(" :", 1)
                if len(msg) == 1:
                    msg = msg[0].split(" ")
                elif len(msg) == 2:
                    msg = msg[0].split(" ") + [msg[1]]
                if msg[0][0] == ':':
                    lines += [{"type":"message", "src":msg[0][1:], "cmd":msg[1], "args":[*msg[2:]]}]
                else:
                    lines += [{"type":"message", "cmd":msg[0], "args":[*msg[1:]]}]
        return lines
    # }}}
    # {{{ queue(self, *args): Parse and queue single line to server from list
    def queue(self, *args):
        msg = ""; argNumMax = len(args);
        for argNum in range(argNumMax):
            if argNum == (argNumMax - 1):
                msg += ":" + args[argNum]
            else:
                msg += args[argNum] + " "
        self.clientQueue.append((msg + "\r\n").encode())
    # }}}
    # {{{ unqueue(self): Send all queued lines to server and return interrupt bit
    def unqueue(self):
        while self.clientQueue:
            msg = self.clientQueue[0]; msgLen = len(msg); msgBytesSent = 0;
            msgBytesSent = self.clientSocket.send(msg)
            if msgBytesSent < msgLen:
                self.clientQueue[0] = msg[msgBytesSent:]; return False;
            elif msgBytesSent == msgLen:
                del self.clientQueue[0]
        return True
    # }}}
    # {{{ __init__(self, hostname, nick, port, realname, user, **kwargs): initialisation method
    def __init__(self, hostname, nick, port, realname, user, **kwargs):
        self.serverHname = hostname; self.serverPort = port;
        self.clientNick = nick; self.clientIdent = user; self.clientGecos = realname;
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120
