```
    _ Supports IPX/_SPX out of _ the box!  Multiplayer on Windows 3.x, RISC OS,
   / \   _ __ __ _| |__   ___ | |_   _          _   _ _____   _____  __
  / _ \ | '__/ _` | '_ \ / _ \| | | | |  Only  | \ | |_   _| |___ / / |   Only
 / ___ \| | | (_| | |_) | (_) | | |_| |  uses  |  \| | | |     |_ \ | | $1495 w/
/_/   \_\_|  \__,_|_.__/ \___/|_|\__, |  16 MB | |\  | | |    ___) || | 6 months
Immaculately crafted 32-bit code!|___/  RAM on |_| \_| |_|   |____(_)_|  phone
  Exquisite 256 colour SVGA graphics!  average!        and VAX/VMS!     support!
               _   _   _   _   _   _   _   _     _   _   _   _   _   _
 More than 92 / \ / \ / \ / \ / \ / \ / \ / \   / \ / \ / \ / \ / \ / \ Not at all
    hidden   ( A | d | v | a | n | c | e | d ) ( S | e | r | v | e | r )  stolen
 cheat codes! \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/   \_/ \_/ \_/ \_/ \_/ \_/  from DEC!

```

**WARNING**: All characters and events in this IRC board game -- especially those based on real people --
are entirely fictional. The game contains coarse language, politically incorrect and universally offensive
humour, extremely unfunny jokes that even the most ordinary hippopotami would categorically refuse to
entertain, and due to its content it should not be played by anyone. If you are affiliated with South(c)
Park(r) Studios(tm), (r)Hasbro(c). (tm)Inc(tm), Mi(c)rosoft(r) Co(r)po(r)a(tm)ion, Digital(c) Equipment(c)
Corporation(c), Hewlett(tm)-Fiorina(c), the Martian Congressional Republic(tm), the Association of Anarchist
Monsters of SandNET, and/or the Shadow Police(tm), please feel free to contact our corporate legal department
at Road of Frozen Despair #1934247, Icy Death Plains County, Central South Pole, South Pole, Chile should you
feel like suing us.

# Araboly NT 3.1 Advanced Server
**Everyone's favourite board game... with IRC support and fancy colours! (WORK IN PROGRESS)**  
Copyright (c) 2018 Lucía Andrea Illanes Albornoz <<lucia@luciaillanes.de>>  
This project is licensed under the terms of the MIT licence.

How to run:
* Command line: ./ArabolyIrcBot.py `<hostname>` [`<port>`] [`<nick name>`] [`<user name>`] [`<IRC real name>`] [`<channel name>`]
* Defaults: [``] [`6667`] [`ARABOLY`] [`ARABOLY`] [`Araboly NT 3.1 Advanced Server`] [`#ARABOLY']
* Prerequisites: Python >=3.5.x

### General IRC commands:
* **.mhelp** -- Display help screen
* **.mpart** -- Leave current game
* **.mstatus** -- Display game and player status

### Bot owner IRC commands:
* **.mkick** *player* -- Kick *player* from game
* **.mstop** -- Stop current game

### Attract mode IRC commands:
* **.mstart** *players* -- Start new game with *players* players
* **.mjoin** -- Join current game

### In-game IRC commands:
* **.mboard** -- Display game board
* **.mcheat** -- Instantly win the game and steal everyone else's everything
* **.mdevelop** *field* *level* -- Develop property on *field* at level *level*
* **.mdice** -- Roll dice, advance player, and process turn

### Property mode IRC commands:
* **.mbuy** -- Buy offered property
* **.mpass** -- Don't buy offered property and enter auction mode

### Auction mode IRC commands:
* **.mbid** *price* -- Bid on property at *price*
* **.mpass** -- Pass on property
