```
       Cat-powered!     _ActiveAraboly _  support  _  out of the box!  Built on NT technology!    100% vegan!
         _     _,      / \   _ __ __ _| |__   ___ | |_   _            ___  ___  ___  ___           ,_     _
         \~-,_//|     / _ \ | '__/ _` | '_ \ / _ \| | | | |  Only    |_  |/ _ \/ _ \/ _ \  Only    |\\_,-~/
 .--,    | _  _ \    / ___ \| | | (_| | |_) | (_) | | |_| |  uses   / __// // / // / // / $3999   / _  _ |    ,--.
 '-, \   ( $  $  )  /_/   \_\_|  \__,_|_.__/ \___/|_|\__, | 128 MB /____/\___/\___/\___/   for   (  %  % )   / ,-'
    ) )_.-\_T_  /   Immaculately crafted 64-bit code!|___/  RAM on                      25 users! \  _T_/-._( (
   / .'         \   Exquisite 24-bit True Colour graphics! average!    Service Pack 4             /         `. \
  | /   _BANKCAT |              _   _   _   _   _   _   _   _     _   _   _   _   _   _          | DICECAT_   \ |
  |      \  , / /  Most secure / \ / \ / \ / \ / \ / \ / \ / \   / \ / \ / \ / \ / \ / \  Almost  \ \ ,  /      |
   \   __/_-| ||   version of ( A | d | v | a | n | c | e | d ) ( S | e | r | v | e | r ) supports || |-_\__   /
    '-,____)'\_)) Araboly yet! \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/   \_/ \_/ \_/ \_/ \_/ \_/   Alpha! ((_/`(____,-'

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

# Araboly 2000 Advanced Server SP4
**Everyone's favourite board game... with IRC support and fancy colours! (WORK IN PROGRESS)**  
Copyright (c) 2018 Lucía Andrea Illanes Albornoz <<lucia@luciaillanes.de>>  
This project is licensed under the terms of the MIT licence.
![Screenshot](https://raw.githubusercontent.com/lalbornoz/araboly/master/assets/images/ArabolyBoardSouth.png "Screenshot")

### How to run:
```
usage: ./ArabolyIrcBot.py [-c <channel name>] [-d] [-C <connect timeout>]
                          [-f <delay in ms>] [-h] [-n <nick name>] [-p <port>]
                          [-r <IRC real name>] [-S] [-u <user name>] -H <hostname>

         -c <channel name>.....:  defaults to #ARABOLY.
         -C <connect timeout>..:  defaults to 15 (seconds.)
         -d ...................:  load snapshot, break into pdb prompt & save snapshot on exception; disabled by default.
         -f <delay in ms>......:  defaults to 0 (disabled.)
         -h ...................:  display this screen.
         -H <hostname>.........:  no default, must always be specified.
         -n <nick name>........:  defaults to ARABOLY.
         -p <port>.............:  defaults to 6667 or 6697 if using SSL.
         -r <IRC real name>....:  defaults to `Araboly 2000 Advanced Server SP4'.
         -R ...................:  record games to savefiles; disabled by default.
         -S ...................:  use SSL; disabled by default.
         -u <user name>........:  defaults to ARABOLY.
```
Requires Python >= v3.5 and YAML.

### General IRC commands:
* **.melp?** -- explodes.
* **.mhelp** -- Display help screen
* **.mpart** -- Leave current game
* **.msave** *filename* -- Saves local snapshot to assets/savefiles/*filename*
* **.mstatus** -- Display game and player status

### Bot owner IRC commands:
* **.mkick** *player* -- Kick *player* from game
* **.mstop** -- Stop current game

### Attract mode IRC commands:
* **.mload** *filename* -- Load local snapshot from assets/savefiles/*filename*
* **.msetup** *max_players* -- Enter new game setup mode; *max_players* defaults to 6

### Game setup mode IRC commands:
* **.mjoin** -- Join game
* **.mstart** -- Start game

### In-game IRC commands:
* **.maccept** *player* -- Accept last trade offer from *player*
* **.mboard** -- Display game board
* **.mbuy** *player* *field* *price* -- Offer/counter-offer to buy *field* from *player* at *price*
* **.mdevelop** *field* *level* -- Develop property on *field* at level *level*
* **.mdice** -- Roll dice, advance player, and process turn
* **.mjoin** -- Join game
* **.mlift** *field* -- Lift mortgaged property *field* at the cost of 50% market value and 10% interest
* **.mmortgage** *field* -- Mortgage *field* property at 50% market value and 10% interest
* **.mreject** *player* -- Reject last trade offer from *player*
* **.msell** *player* *field* *price* -- Offer/counter-offer to sell *field* to *player* at *price*

### Property mode IRC commands:
* **.mbuy** -- Buy offered property
* **.mpass** -- Don't buy offered property and enter auction mode

### Auction mode IRC commands:
* **.mbid** *price* -- Bid on property at *price*
* **.mpass** -- Pass on property

### Bankruptcy mode IRC commands:
* **.mmortgage** *field* -- Mortgage *field* property at 50% market value and 10% interest
