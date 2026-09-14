# Waiting Rooms Board

A browser editor for the room boards that They Are Waiting deals its levels
from. Open `index.html` (or the hosted page), paint rooms into the slots,
and use **Download for the game** to save a `.json` board. Drop that file
into the game's `boards/` folder and its rooms are dealt with everyone
else's.

Boards are kept in your browser. Download a board to keep a copy or to hand
it to someone else; **Import a board** takes a downloaded `.json` or the text
of a `.tscn` board.

To refresh the tile sheets and the game's boards after the game's art, main
board or tutorial changes, run `python3 refresh_from_game.py /path/to/the/game`
here and push.

## Live shared saving

With a free Firebase project behind it, every visitor's boards save live to
the same place, the board list updates for everyone, and one person edits a
board at a time.

1. Go to https://console.firebase.google.com, add a project (any name, no
   analytics needed).
2. Build, Firestore Database, Create database, start in **production mode**.
3. On the database's Rules tab, replace the rules with:

       rules_version = '2';
       service cloud.firestore {
         match /databases/{database}/documents {
           match /{document=**} {
             allow read, write: if true;
           }
         }
       }

   and publish them. This lets anyone who has the site's address read and
   change the boards and sheets, which is the point for a shared editor; keep
   the address among the people who should have it.
4. Project settings (the cog), Your apps, add a **Web** app, and copy the
   `firebaseConfig` object it shows.
5. Paste it into `firebase-config.js` in place of `null` and push the site.

The page then says "saved to the cloud" after each change.

## The artist's sheets

**Add sheet** turns a PNG into a new tile sheet (every cell with paint in it
is a tile), and **Replace this sheet** swaps the art of the sheet on show for
a new PNG, in place, so rooms already painted from it show the new art. Both
are saved with the boards.

To put that art into the game, **Download sheets for the game** saves
`sheets.json`; in the game repository run

    python3 tools/import_sheets.py sheets.json

which writes the PNGs into the project and adds or refreshes the tileset's
sources. Open the project in Godot once so it imports the images, then run
`python3 refresh_from_game.py /path/to/the/game` here and push, so the
editor ships the new art as well.

## Backups

`.github/workflows/board-backup.yml` runs `backup.py` every four hours and
commits the shared boards and sheets under `backups/` whenever they changed.
Turn it on once: Settings, Actions, General, "Read and write permissions"
under Workflow permissions; then Actions, Board backup, Run workflow.
