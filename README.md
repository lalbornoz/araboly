```
       Cat-powered!     _ Supports IPX/_SPX out of _ the box!  Multiplayer on Windows 3.x, RISC OS,     100% vegan!
         _     _,      / \   _ __ __ _| |__   ___ | |_   _          _   _ _____   _  _    ___              ,_     _
         \~-,_//|     / _ \ | '__/ _` | '_ \ / _ \| | | | |  Only  | \ | |_   _| | || |  / _ \    Only     |\\_,-~/
 .--,    | _  _ \    / ___ \| | | (_| | |_) | (_) | | |_| |  uses  |  \| | | |   | || |_| | | | $1495 w/   / _  _ |    ,--.
 '-, \   ( @  @  )  /_/   \_\_|  \__,_|_.__/ \___/|_|\__, |  16 MB | |\  | | |   |__   _| |_| | 6 month   (  @  @ )   / ,-'
    ) )_.-\_T_  /   Immaculately crafted 32-bit code!|___/  RAM on |_| \_| |_|      |_|(_)___/   phone     \  _T_/-._( (
   / .'         \    Exquisite 256 colour SVGA graphics!   average!       and VAX/VMS!          support!  /         `. \
  | /   _BANKCAT |                _   _   _   _   _   _   _   _     _   _   _   _   _   _                | DICECAT_   \ |
  |      \  , / /   More than 92 / \ / \ / \ / \ / \ / \ / \ / \   / \ / \ / \ / \ / \ / \ Not at all     \ \ ,  /      |
   \   __/_-| ||       hidden   ( A | d | v | a | n | c | e | d ) ( S | e | r | v | e | r )  stolen        || |-_\__   /
    '-,____)'\_))   cheat codes! \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/   \_/ \_/ \_/ \_/ \_/ \_/  from DEC!     ((_/`(____,-'
    
       **WARNING**:  All characters and events in this IRC board game -- especially those based on real people --
       are entirely fictional. The game contains coarse language, politically incorrect and universally offensive
          humour, extremely unfunny jokes that even the most ordinary hippopotami would categorically refuse to
         entertain, and due to its content it should not be played by anyone. If you are affiliated with South(c)
        Park(r) Studios(tm), (r)Hasbro(c). (tm)Inc(tm), Mi(c)rosoft(r) Co(r)po(r)a(tm)ion, Digital(c) Equipment(c)
       Corporation(c), Hewlett(tm)-Fiorina(c), the Martian Congressional Republic(tm), the Association of Anarchist
       Monsters of SandNET (AAMS(c),) and/or the Shadow Police(tm), please feel free to contact our corporate legal
      department at Road of Frozen Despair #19342457, Icy Death Plains County, Central South Pole, South Pole, Chile
                                              should you feel like suing us.
```

# Araboly NT 4.0 Advanced Server
**Everyone's favourite board game... with IRC support and fancy colours! (WORK IN PROGRESS)**  
Copyright (c) 2018 Lucía Andrea Illanes Albornoz <<lucia@luciaillanes.de>>  
This project is licensed under the terms of the MIT licence.
![Screenshot](https://raw.githubusercontent.com/lalbornoz/araboly/master/assets/ArabolyBoardSouth.png "Screenshot")

### How to run:
```
usage: ./ArabolyIrcBot.py [-c <channel name>] [-d] [-f <delay in ms>]  [-h]
                          [-n <nick name>] [-p <port>] [-r <IRC real name>]
                          [-S] [-u <user name>] -H <hostname>
         -c <channel name>.:  defaults to #ARABOLY.
         -d ...............:  debugging mode; disabled by default.
         -f <delay in ms>..:  defaults to 0 (disabled.)
         -n <nick name>....:  defaults to ARABOLY.
         -p <port>.........:  defaults to 6667 or 6697 if using SSL.
         -r <IRC real name>:  defaults to `Araboly NT 4.0 Advanced Server'.
         -S ...............:  use SSL; disabled by default.
         -u <user name>....:  defaults to ARABOLY.

WARNING: Do _not_ under any circumstances share, send, receive, download, etc. pp. the
snapshot file created whenever an exception is raised during debugging (-d) mode, as the
object {,de}serialisation Python module employed is `not intended to be secure against
erroneous or maliciously constructed data. Never unpickle data received from an untrusted
or unauthenticated source.' (The Python Standard Library » 11.1. pickle — Python object serialization)
```
Requires Python >= v3.5.

### General IRC commands:
* **.melp?** -- explodes.
* **.mhelp** -- Display help screen
* **.mpart** -- Leave current game
* **.mstatus** -- Display game and player status

### Bot owner IRC commands:
* **.mkick** *player* -- Kick *player* from game
* **.mstop** -- Stop current game

### Attract mode IRC commands:
* **.mstart** *players* -- Start new game with *players* players

### Game setup mode IRC commands:
* **.mjoin** -- Join game

### In-game IRC commands:
* **.maccept** *player* -- Accept last trade offer from *player*
* **.mboard** -- Display game board
* **.mcheat** -- Instantly win the game and steal everyone else's everything
* **.mdevelop** *field* *level* -- Develop property on *field* at level *level*
* **.mdice** -- Roll dice, advance player, and process turn
* **.mlift** *field* -- Lift mortgaged property *field* at the cost of 50% market value and 10% interest
* **.mmortgage** *field* -- Mortgage *field* property at 50% market value and 10% interest
* **.moffer** *buy/sell* *player* *field* *price* -- Offer/counter-offer to buy/sell *field* from/to *player* at *price*
* **.mreject** *player* -- Reject last trade offer from *player*

### Property mode IRC commands:
* **.mbuy** -- Buy offered property
* **.mpass** -- Don't buy offered property and enter auction mode

### Auction mode IRC commands:
* **.mbid** *price* -- Bid on property at *price*
* **.mpass** -- Pass on property

### Bankruptcy mode IRC commands:
* **.mmortgage** *field* -- Mortgage *field* property at 50% market value and 10% interest
