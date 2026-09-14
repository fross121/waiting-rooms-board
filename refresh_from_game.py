"""Refresh this editor's data from the game project: the tileset manifest, a
copy of every sheet it draws from, and the game's own boards (the main room
board and the tutorial level) as the editor's editable starting copies.

  python3 refresh_from_game.py /path/to/They-are-waiting

Run it whenever the game's tileset, a sheet, rooms.tscn or the tutorial
changes, then commit and push this repository. index.html is untouched.
"""
import json, os, re, shutil, sys

if len(sys.argv) < 2 or not os.path.isdir(os.path.join(sys.argv[1], "tilesets")):
    sys.exit(__doc__)
GAME = os.path.abspath(sys.argv[1])
OUT = os.path.dirname(os.path.abspath(__file__))

tres = open(os.path.join(GAME, "tilesets", "facility_tileset.tres")).read()
ext = {}
for m in re.finditer(r'\[ext_resource type="Texture2D"(?: uid="[^"]*")? path="res://([^"]+)" id="([^"]+)"\]', tres):
    ext[m.group(2)] = m.group(1)
subs = {}
for m in re.finditer(r'\[sub_resource type="TileSetAtlasSource" id="([^"]+)"\]\n((?:.+\n)+?)(?=\n)', tres):
    body = m.group(2)
    tex = re.search(r'texture = ExtResource\("([^"]+)"\)', body).group(1)
    size = re.search(r'texture_region_size = Vector2i\((\d+), (\d+)\)', body)
    tiles = re.findall(r'^(\d+):(\d+)/0 = 0$', body, re.M)
    subs[m.group(1)] = {"texture": ext[tex],
                        "region": [int(size.group(1)), int(size.group(2))] if size else [16, 16],
                        "tiles": [[int(a), int(b)] for a, b in tiles]}
manifest = {"sources": {}}
for m in re.finditer(r'^sources/(\d+) = SubResource\("([^"]+)"\)$', tres, re.M):
    sid, s = int(m.group(1)), dict(subs[m.group(2)])
    s["file"] = "sheet_%d.png" % sid
    shutil.copyfile(os.path.join(GAME, s["texture"]), os.path.join(OUT, s["file"]))
    manifest["sources"][str(sid)] = s
with open(os.path.join(OUT, "manifest.js"), "w") as f:
    f.write("window.TILESET = " + json.dumps(manifest, separators=(",", ":")) + ";\n")


def scene_board(scene, name, var, out_name):
    text = open(os.path.join(GAME, "scenes", scene)).read()
    layers = {m.group(1): m.group(2) for m in re.finditer(
        r'\[node name="(\w+)" type="TileMapLayer"[^\]]*\]\n(?:.*\n)*?tile_map_data = PackedByteArray\("([^"]*)"\)', text)}
    board = {"format": "tawboard/1", "name": name, "author": "Fred", "layers": layers}
    with open(os.path.join(OUT, out_name), "w") as f:
        f.write("window.%s = " % var + json.dumps(board, separators=(",", ":")) + ";\n")
    return layers


main = scene_board("rooms.tscn", "Main board (rooms.tscn)", "MAIN_BOARD", "main_board.js")
tut = scene_board("tutorial_level.tscn", "Tutorial level", "TUTORIAL_BOARD", "tutorial_board.js")
print("refreshed: %d sources, main board %d layers, tutorial %d layers" % (len(manifest["sources"]), len(main), len(tut)))
