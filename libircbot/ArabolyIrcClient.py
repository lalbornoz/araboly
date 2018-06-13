#!/usr/bin/env python3
#
# Araboly 2000 Advanced Server SP3 -- everyone's favourite board game... with IRC support and fancy colours!
# Copyright (c) 2018 Lucía Andrea Illanes Albornoz <lucia@luciaillanes.de>
# This project is licensed under the terms of the MIT licence.
#

import select, socket, ssl

class ArabolyIrcClient(object):
    """Non-blocking abstraction over the IRC protocol"""

    # {{{ close(self): Close connection to server
    def close(self):
        if self.clientSocket != None:
            self.clientSocket.close()
        self.clientSocket = None
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
        if self.sslFlag:
            self.clientSocket = ssl.wrap_socket(self.clientSocket, do_handshake_on_connect=False)
            while True:
                try:
                    self.clientSocket.do_handshake()
                    break
                except ssl.SSLWantReadError:
                    readySet = select.select([], [self.clientSocket.fileno()], [], timeout)
        self.clientQueue = []
        self.queue("NICK", [self.clientNick])
        self.queue("USER", [self.clientIdent, "0", "0", self.clientGecos])
        return True
    # }}}
    # {{{ readlines(self): Read and parse lines from server into list of canonicalised lists
    def readlines(self):
        lines = []
        while True:
            try:
                if len(self.partialLine) >= 512:
                    raise ValueError
                newLines = self.clientSocket.recv(512 - len(self.partialLine))
            except ssl.SSLWantReadError:
                return lines
            except BlockingIOError:
                return lines
            except ValueError:
                self.partialLine = 0; continue;
            if newLines == None:
                lines += [None]; break;
            elif len(newLines) == 0:
                break
            else:
                newLines = str(newLines, "utf-8")
                if newLines[-2:] == "\r\n":
                    msgs = (self.partialLine + newLines).split("\r\n")[0:-1]
                    self.partialLine = ""
                else:
                    msgs = (self.partialLine + newLines).split("\r\n")
                    if len(msgs) > 1:
                        self.partialLine = msgs[-1]; msgs = msgs[0:-1];
                    else:
                        self.partialLine += msgs[0]; msgs = [];
                for msg in msgs:
                    msg = msg.split(" :", 1)
                    if len(msg) == 1:
                        msg = msg[0].split(" ")
                    elif len(msg) == 2:
                        msg = msg[0].split(" ") + [msg[1]]
                    newLine = {"idFull":[self.clientNick, self.clientIdent, self.clientHost], "eventType":"message"}
                    if msg[0][0] == ':':
                        newLine.update({"args":[*msg[2:]], "cmd":msg[1], "src":msg[0][1:]})
                    else:
                        newLine.update({"args":[*msg[1:]], "cmd":msg[0]})
                    if self._clientHostHook(newLine):
                        lines += [newLine]
        return lines
    # }}}
    # {{{ queue(self, cmd, args): Parse and queue single line to server from list
    def queue(self, cmd, args):
        msg = cmd; msg += " " + " ".join(args[:-1]) if len(args) > 1 else "";
        if len(args):
            if " " in args[-1]:
                if cmd.upper() == "NOTICE" or cmd.upper() == "PRIVMSG":
                    msgPfx = ":{}!{}@{} {} :".format(self.clientNick, self.clientIdent, self.clientHost, msg)
                    msgPfxLen = len(msgPfx.encode())
                    msgLen = msgPfxLen + len(args[-1].encode())
                    if msgLen > 512:
                        lastArgs = args[-1].encode()
                        splitLen = 512 - len("\r\n") - msgPfxLen
                        for idx in range(0, len(lastArgs), splitLen):
                            lastArg = lastArgs[idx:idx+splitLen]
                            self.queue(cmd, [*args[:-1], lastArg.decode()])
                        return
                msg += " :" + args[-1]
            else:
                msg += " " + args[-1]
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
    # {{{ _clientHostHook(self, msg): XXX
    def _clientHostHook(self, msg):
        if   msg["cmd"] == "001":
            self.queue("PRIVMSG", [self.clientNick, "\x01CLIENTHOSTHOOK\x01"])
        elif msg["cmd"].upper() == "NICK":
            prefix = "{}!{}@{}".format(self.clientNick, self.clientIdent, self.clientHost)
            if msg["src"].lower() == prefix.lower():
                self.clientNick = msg["args"][0].split("!")[0]
        elif msg["cmd"].upper() == "PRIVMSG"                    \
        and  msg["args"][0].lower() == self.clientNick.lower()  \
        and  msg["args"][1] == "\x01CLIENTHOSTHOOK\x01":
            self.clientNick = msg["src"]
            if "!" in self.clientNick:
                self.clientNick, self.clientIdent = self.clientNick.split("!")
                if "@" in self.clientIdent:
                    self.clientIdent, self.clientHost = self.clientIdent.split("@")
            return False
        return True
    # }}}
    # {{{ __init__(self, hostname, nick, port, realname, user, ssl=False, **kwargs): initialisation method
    def __init__(self, hostname, nick, port, realname, user, ssl=False, **kwargs):
        self.serverHname = hostname; self.serverPort = port;
        self.clientNick = nick; self.clientIdent = user; self.clientGecos = realname; self.clientHost = "";
        self.clientSocket = self.clientQueue = None;
        self.partialLine = ""; self.sslFlag = ssl;
    # }}}

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=0
