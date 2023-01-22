# Engaging Math Game

## The game rules

This is a simple turn based game with the following setup:
* Two players go against each other, taking turns, picking tiles from a 8 by 8 board and adding the tile values to their score.
* At the start of the game the board is filled with numbered tiles and a single tile with a smiley face.
* One of the players will only be able to pick tiles from the row that contains the smiley face tile, the other player will only be able to pick tiles from  the column that contains the smiley face tile.
* The heading of each player (rows or columns) is chosen at random at the begining of the game
* Who goes first is chosen at random at the begining of the game.
* The player who currently has the right of play selects a **numbered** tile from their heading. The number on the selected tile is added to the player's score. The selected tile is removed from the board and the smiley face tile is moved to its place. The position that was previously occupied by the smiley face tile is now marked as empty.
* Both the smiley face tile and any empty tile are unavailable to be picked up.
* If the current player has no valid moves, they skip a turn.
* The game ends once both players have no valid moves. The player with the higher score is the winner.

## Implementation details

This implementation is composed of a client with GUI that connects to a server which hosts the games. The GUI relies on `pygame`. The communication between the client and the server is handled by a very unsafe protocol comprised of a plain TCP connection which transfers the needed data which is `pickle`'d.
