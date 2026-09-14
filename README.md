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
           match /boards/{board} {
             allow read, write: if true;
           }
         }
       }

   and publish them. This lets anyone who has the site's address read and
   change the boards, which is the point for a shared editor; keep the
   address among the people who should have it.
4. Project settings (the cog), Your apps, add a **Web** app, and copy the
   `firebaseConfig` object it shows.
5. Paste it into `firebase-config.js` in place of `null` and push the site.

The page then says "saved to the cloud" after each change.
