#!/usr/bin/env python3
"""Render index.html from menu.json (source of truth).
Other agents: add entries to menu.json (or use publish-page.sh), then run:
  python3 tools/build_menu.py            # rebuild index.html
  python3 tools/build_menu.py add <dir> <section-name> <title> <path> <date>
Never hand-edit index.html; it is overwritten."""
import json, sys, html, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MENU = os.path.join(ROOT, "menu.json")

def load():
    with open(MENU, encoding="utf-8") as f: return json.load(f)

def save(m):
    tmp = MENU + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f: json.dump(m, f, ensure_ascii=False, indent=2); f.write("\n")
    os.replace(tmp, MENU)

def add(m, d, name, title, path, date):
    sec = next((s for s in m["sections"] if s["dir"] == d), None)
    if sec is None:
        sec = {"dir": d, "name": name or d, "pages": []}; m["sections"].append(sec)
    if not any(p["path"] == path for p in sec["pages"]):
        sec["pages"].insert(0, {"title": title, "path": path, "date": date})

def render(m):
    e = html.escape
    secs = []
    for s in m["sections"]:
        items = "".join(
            f'<li><a href="{e(p["path"])}"><span class="pt">{e(p["title"])}</span>'
            f'<span class="pd">{e(p.get("date",""))}</span></a></li>' for p in s["pages"])
        secs.append(f'<section class="card"><h2>{e(s["name"])}</h2><ul>{items}</ul></section>')
    return f'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{e(m["title"])}</title>
<!-- GENERATED from menu.json by tools/build_menu.py — do not edit by hand -->
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:"PingFang SC","Hiragino Sans GB","Noto Sans CJK SC","Microsoft YaHei",sans-serif;background:#fff7f0;color:#222;font-size:17px;line-height:1.6}}
.wrap{{max-width:480px;margin:0 auto;padding:18px 14px 30px}}
h1{{font-size:22px;color:#e8630a;margin-bottom:14px}}
.card{{background:#fff;border-radius:14px;padding:14px;margin-bottom:12px;box-shadow:0 2px 6px rgba(0,0,0,.06)}}
h2{{display:inline-block;font-size:16px;color:#fff;background:#e8630a;border-radius:12px;padding:3px 10px;margin-bottom:8px}}
ul{{list-style:none}}
li a{{display:flex;flex-direction:column;min-height:48px;padding:10px 12px;margin-top:8px;border-radius:10px;background:#fff3e8;color:#222;text-decoration:none}}
li a:active{{background:#ffe2c6}}
.pt{{font-size:17px;font-weight:700;color:#c4520a}}
.pd{{font-size:16px;color:#888}}
</style></head><body><main class="wrap">
<h1>{e(m["title"])}</h1>
{"".join(secs)}
</main></body></html>
'''

if __name__ == "__main__":
    m = load()
    if len(sys.argv) > 1 and sys.argv[1] == "add":
        add(m, *sys.argv[2:7]); save(m)
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f: f.write(render(m))
    print("index.html rebuilt:", sum(len(s["pages"]) for s in m["sections"]), "pages")
