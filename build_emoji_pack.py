#!/usr/bin/env python3
"""
build_emoji_pack.py
Jalanin: python build_emoji_pack.py /path/ke/twemoji/assets/72x72
Output: ./java_pack/ dan ./bedrock_pack/ siap zip & pasang.
"""
import sys, os, json
from PIL import Image
from emoji_map import EMOJI_MAP

CELL = 32
GRID = 16
SHEET_SIZE = CELL * GRID

def load_twemoji(src_dir, codepoint_filename):
    path = os.path.join(src_dir, f"{codepoint_filename}.png")
    if not os.path.exists(path):
        print(f"  [!] Gak ketemu: {codepoint_filename}.png — skip")
        return None
    return Image.open(path).convert("RGBA")

def build(src_dir):
    java_font_dir = "java_pack/assets/minecraft/textures/font/emoji"
    java_root = "java_pack/assets/minecraft"
    bedrock_root = "bedrock_pack/font"
    os.makedirs(java_font_dir, exist_ok=True)
    os.makedirs(f"{java_root}/font", exist_ok=True)
    os.makedirs(bedrock_root, exist_ok=True)

    sheet = Image.new("RGBA", (SHEET_SIZE, SHEET_SIZE), (0, 0, 0, 0))
    providers = [{"type": "reference", "id": "minecraft:include/default"}]

    for emoji, cp_file, pua_hex in EMOJI_MAP:
        img = load_twemoji(src_dir, cp_file)
        if img is None:
            continue
        resized = img.resize((CELL, CELL), Image.LANCZOS)

        resized.save(f"{java_font_dir}/{pua_hex}.png")
        providers.append({
            "type": "bitmap",
            "file": f"minecraft:font/emoji/{pua_hex}.png",
            "ascent": 8,
            "height": 9,
            "chars": [f"\\u{pua_hex}"]
        })

        code = int(pua_hex, 16) & 0xFF
        row, col = code >> 4, code & 0xF
        sheet.paste(resized, (col * CELL, row * CELL), resized)

        print(f"  [+] {emoji} -> U+{pua_hex}")

    with open(f"{java_root}/font/default.json", "w", encoding="utf-8") as f:
        json.dump({"providers": providers}, f, indent=2, ensure_ascii=False)

    with open("java_pack/pack.mcmeta", "w") as f:
        json.dump({"pack": {"pack_format": 48, "description": "AztheraSMP Fishing Emoji Pack"}}, f, indent=2)

    sheet.save(f"{bedrock_root}/glyph_E0.png")
    manifest = {
        "format_version": 2,
        "header": {
            "name": "AztheraSMP Fishing Emoji Pack",
            "description": "Custom emoji glyphs - sync with Java pack",
            "uuid": "b7a1d3e2-4c5f-4a8e-9b2d-1f6e8c3a7d10",
            "version": [1, 0, 0],
            "min_engine_version": [1, 20, 0]
        },
        "modules": [{"type": "resources", "uuid": "e2f4a6b8-7c9d-4e1f-8a3b-5d6c9e2f4a18", "version": [1, 0, 0]}]
    }
    with open("bedrock_pack/manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    print("\nDone. java_pack/ dan bedrock_pack/ siap di-zip.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python build_emoji_pack.py <path_ke_folder_72x72>")
        sys.exit(1)
    build(sys.argv[1])
