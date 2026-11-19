#!/usr/bin/env python3
"""Importiert die Blogbeiträge der alten WordPress-Seite nach _posts/.

Nutzung:
  python3 tools/import_wordpress.py                 # lädt live über die WP-REST-API
  python3 tools/import_wordpress.py --from-dir DIR  # nutzt gespeicherte posts1.json, posts2.json, cats.json, tags.json

Die Permalinks bleiben identisch zu WordPress (/<slug>/), damit Google-Rankings
und Backlinks der Beiträge ohne Weiterleitung erhalten bleiben.
Bilder werden vorerst von www.startupdorf.de/wp-content/ eingebunden
(siehe docs/MIGRATION.md – vor Abschaltung von WordPress herunterladen!).
"""
import argparse
import html
import json
import os
import re
import sys
import urllib.request

API = "https://www.startupdorf.de/wp-json/wp/v2"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "_posts")

GERMAN_WORDS = {"und", "der", "die", "das", "ist", "nicht", "mit", "für", "auf", "wir", "ein", "eine", "sich", "auch", "von", "zu", "den", "im", "wird", "sind"}
ENGLISH_WORDS = {"and", "the", "is", "not", "with", "for", "on", "we", "an", "of", "to", "our", "are", "will", "you", "this"}


def fetch(path):
    req = urllib.request.Request(f"{API}/{path}", headers={"User-Agent": "startupdorf-site-import"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def load(from_dir):
    if from_dir:
        posts = []
        for name in sorted(os.listdir(from_dir)):
            if re.match(r"posts\d+\.json$", name):
                posts += json.load(open(os.path.join(from_dir, name), encoding="utf-8"))
        cats = json.load(open(os.path.join(from_dir, "cats.json"), encoding="utf-8"))
        tags = json.load(open(os.path.join(from_dir, "tags.json"), encoding="utf-8"))
        return posts, cats, tags
    posts, page = [], 1
    while True:
        batch = fetch(f"posts?per_page=100&page={page}&_embed=1")
        posts += batch
        if len(batch) < 100:
            break
        page += 1
    return posts, fetch("categories?per_page=100"), fetch("tags?per_page=100")


def text_of(fragment):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", fragment))).strip()


def detect_lang(text):
    words = re.findall(r"[a-zäöüß]+", text.lower())
    de = sum(w in GERMAN_WORDS for w in words)
    en = sum(w in ENGLISH_WORDS for w in words)
    return "de" if de >= en else "en"


def clean_content(c):
    c = re.sub(r"(?is)<script\b.*?</script>", "", c)
    c = re.sub(r"(?is)<style\b.*?</style>", "", c)
    c = re.sub(r"(?is)<noscript\b.*?</noscript>", "", c)
    c = re.sub(r"\[/?tboot_[a-z_]+[^\]]*\]", "", c)          # Theme-Shortcodes entfernen, Inhalt behalten
    c = re.sub(r' class="isSelectedEnd"', "", c)
    c = re.sub(r' data-spread="(?:true|false)"', "", c)
    c = re.sub(r'(src|href|srcset)="/wp-content/', r'\1="https://www.startupdorf.de/wp-content/', c)  # relative WP-Pfade absolut machen
    c = c.replace("www.youtube.com/embed/", "www.youtube-nocookie.com/embed/")
    c = re.sub(r"<img\b(?![^>]*\bloading=)", '<img loading="lazy"', c)
    c = re.sub(r"<iframe\b(?![^>]*\bloading=)", '<iframe loading="lazy"', c)
    c = re.sub(r"\n{3,}", "\n\n", c)
    return c.strip() + "\n"


def yaml_str(s):
    return json.dumps(s, ensure_ascii=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-dir")
    args = ap.parse_args()
    posts, cats, tags = load(args.from_dir)
    cat_names = {c["id"]: html.unescape(c["name"]) for c in cats}
    tag_names = {t["id"]: html.unescape(t["name"]) for t in tags}
    os.makedirs(OUT, exist_ok=True)
    for p in posts:
        slug = p["slug"]
        title = text_of(p["title"]["rendered"])
        content = clean_content(p["content"]["rendered"])
        plain = text_of(content)
        desc = (p.get("yoast_head_json") or {}).get("description") or text_of(p["excerpt"]["rendered"])
        desc = re.sub(r"\s*\[(?:…|&hellip;|\.\.\.)\]\s*$", "…", desc)
        if len(desc) > 160:
            desc = desc[:157].rsplit(" ", 1)[0] + " …"
        emb = p.get("_embedded", {})
        image = None
        fm = emb.get("wp:featuredmedia") or []
        if fm and isinstance(fm[0], dict):
            image = fm[0].get("source_url")
        author = (emb.get("author") or [{}])[0].get("name")
        categories = [cat_names[i] for i in p.get("categories", []) if i in cat_names and cat_names[i] != "Other"]
        post_tags = [tag_names[i] for i in p.get("tags", []) if i in tag_names]
        lines = [
            "---",
            f"title: {yaml_str(title)}",
            f"date: {p['date_gmt'].replace('T', ' ')} +0000",
            f"permalink: /{slug}/",
            f"lang: {detect_lang(plain)}",
            f"description: {yaml_str(desc)}",
        ]
        if image:
            lines.append(f"image: {yaml_str(image)}")
        if author and author not in ("admin",):
            lines.append(f"author: {yaml_str(author)}")
        lines.append(f"categories: {json.dumps(categories, ensure_ascii=False)}")
        if post_tags:
            lines.append(f"tags: {json.dumps(post_tags, ensure_ascii=False)}")
        lines += [
            f"wp_id: {p['id']}",
            f"wp_url: {yaml_str(p['link'])}",
            "render_with_liquid: false",
            "---",
            "",
        ]
        fname = f"{p['date'][:10]}-{slug[:80]}.html"
        with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + content)
    print(f"{len(posts)} Beiträge nach {OUT} geschrieben", file=sys.stderr)


if __name__ == "__main__":
    main()
