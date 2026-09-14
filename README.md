# Waiting Rooms Board

A browser editor for the room boards that They Are Waiting deals its levels
from. Open `index.html` (or the hosted page), paint rooms into the slots,
and use **Download for the game** to save a `.json` board. Drop that file
into the game's `boards/` folder and its rooms are dealt with everyone
else's.

Boards are kept in your browser. Download a board to keep a copy or to hand
it to someone else; **Import a board** takes a downloaded `.json` or the text
of a `.tscn` board.

To refresh the tile sheets and the reference board after the game's art or
main board changes, run `python3 tools/board_editor_data.py` in the game
repository and copy this folder again.
