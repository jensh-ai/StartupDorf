#!/usr/bin/env python3
"""Holt Bilder und PDFs der Blogbeiträge vom alten WordPress-Server ins Repo.

Läuft nach tools/import_wordpress.py:
  python3 tools/localize_images.py [--cache DIR] [--max 1600] [--quality 80]

Was passiert:
- Alle Verweise auf https://www.startupdorf.de/wp-content/uploads/... in _posts/ werden gesammelt.
- Pro Bild wird das Original geladen (WordPress-Größenvarianten wie -1024x683 werden auf das
  Original zurückgeführt). Fehlt das Original, wird die verlinkte Variante genommen.
- Bilder werden auf max. 1600 px verkleinert und als WebP unter assets/uploads/JJJJ/MM/ gespeichert,
  PDFs unverändert kopiert.
- Die Beiträge werden umgeschrieben: lokale Pfade, srcset/sizes entfernt (es gibt nur noch eine Größe).
- Bilder, die schon auf dem alten Server fehlen (404), werden aus den Beiträgen entfernt.
- Ein Bericht landet in docs/bilder-import.md.

Pip-Abhängigkeit: Pillow.
"""
import argparse
import concurrent.futures as cf
import hashlib
import io
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from PIL import Image, ImageSequence

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS = os.path.join(ROOT, "_posts")
OUT = os.path.join(ROOT, "assets", "uploads")
PREFIX = "https://www.startupdorf.de/wp-content/uploads/"
URL_RE = re.compile(r"https?://www\.startupdorf\.de/wp-content/uploads/[^\"'\s)<>,]+")
SIZE_RE = re.compile(r"-\d+x\d+(?=\.[A-Za-z0-9]+$)")
IMG_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
DOC_EXT = {".pdf"}


def fetch(url, cache):
    """Lädt url in den Cache. Gibt Pfad oder None (nicht vorhanden) zurück."""
    key = hashlib.sha1(url.encode()).hexdigest()
    path = os.path.join(cache, key)
    if os.path.exists(path):
        return path
    if os.path.exists(path + ".missing"):
        return None
    quoted = urllib.parse.quote(url, safe=":/%")
    req = urllib.request.Request(quoted, headers={"User-Agent": "startupdorf-site-import"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
    except urllib.error.HTTPError as e:
        if e.code in (403, 404, 410):
            open(path + ".missing", "w").close()
            return None
        raise
    with open(path + ".part", "wb") as f:
        f.write(data)
    os.replace(path + ".part", path)
    return path


def is_animated(im):
    return getattr(im, "is_animated", False) and getattr(im, "n_frames", 1) > 1


def convert(src_path, dest_base, max_px, quality):
    """Konvertiert nach WebP (Animationen bleiben als GIF). Gibt Dateiendung zurück."""
    im = Image.open(src_path)
    if im.format == "GIF" and is_animated(im):
        dest = dest_base + ".gif"
        with open(src_path, "rb") as s, open(dest, "wb") as d:
            d.write(s.read())
        return ".gif"
    im = next(iter(ImageSequence.Iterator(im))).copy() if is_animated(im) else im
    has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
    im = im.convert("RGBA" if has_alpha else "RGB")
    im.thumbnail((max_px, max_px), Image.LANCZOS)
    im.save(dest_base + ".webp", "WEBP", quality=quality, method=6)
    return ".webp"


def local_name(original_url):
    rel = urllib.parse.unquote(original_url[len(PREFIX):])
    parts = rel.split("/")
    if len(parts) >= 3 and parts[0].isdigit() and parts[1].isdigit():
        folder, name = "/".join(parts[:2]), parts[-1]
    else:  # z. B. uploads/formidable/...
        folder, name = "misc", parts[-1]
    stem, ext = os.path.splitext(name)
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", stem).strip("-.") or "bild"
    return folder, stem, ext.lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=os.path.join(ROOT, ".cache", "wp-uploads"))
    ap.add_argument("--max", type=int, default=1600)
    ap.add_argument("--quality", type=int, default=80)
    args = ap.parse_args()
    os.makedirs(args.cache, exist_ok=True)

    files = sorted(os.path.join(POSTS, f) for f in os.listdir(POSTS))
    texts = {f: open(f, encoding="utf-8").read() for f in files}
    urls = set()
    for t in texts.values():
        urls.update(u.rstrip(".") for u in URL_RE.findall(t))

    # Original-URL je Verweis ermitteln
    originals = {u: SIZE_RE.sub("", u) for u in urls}
    wanted = sorted(set(originals.values()) | urls)

    print(f"{len(urls)} Verweise, {len(set(originals.values()))} Originale – lade …", file=sys.stderr)
    with cf.ThreadPoolExecutor(max_workers=12) as ex:
        cached = dict(zip(wanted, ex.map(lambda u: fetch(u, args.cache), wanted)))

    # Quelle pro Original bestimmen und konvertieren
    mapping, missing, used_names, produced = {}, set(), {}, set()
    total_in = total_out = 0
    for u in sorted(urls):
        orig = originals[u]
        folder, stem, ext = local_name(orig)
        if ext not in IMG_EXT | DOC_EXT:
            continue
        src = cached.get(orig) or cached.get(u)
        if not src:
            missing.add(u)
            continue
        key = (folder, stem, ext)
        if key not in used_names:
            dest_dir = os.path.join(OUT, folder)
            os.makedirs(dest_dir, exist_ok=True)
            target_ext = ext if ext in DOC_EXT else ".webp"
            if f"{folder}/{stem}{target_ext}" in produced:  # z. B. bild.jpg und bild.png
                stem = f"{stem}-{ext[1:]}"
            produced.add(f"{folder}/{stem}{target_ext}")
            dest_base = os.path.join(dest_dir, stem)
            if ext in DOC_EXT:
                with open(src, "rb") as s, open(dest_base + ext, "wb") as d:
                    d.write(s.read())
                new_ext = ext
            else:
                try:
                    new_ext = convert(src, dest_base, args.max, args.quality)
                except Exception as e:  # defekte Datei
                    print(f"  ! {orig}: {e}", file=sys.stderr)
                    missing.add(u)
                    continue
            total_in += os.path.getsize(src)
            total_out += os.path.getsize(dest_base + new_ext)
            used_names[key] = f"/assets/uploads/{folder}/{stem}{new_ext}"
        mapping[u] = used_names[key]

    # Beiträge umschreiben
    changed = 0
    for f, t in texts.items():
        new = t
        # Bilder, die fehlen, komplett entfernen
        def drop_missing(m):
            tag = m.group(0)
            srcs = re.findall(r'\bsrc="([^"]+)"', tag)
            return "" if srcs and srcs[0].rstrip(".") in missing else tag
        new = re.sub(r"<img\b[^>]*>", drop_missing, new)
        new = re.sub(r"<a\b[^>]*>\s*</a>", "", new)
        new = re.sub(r"<figure\b[^>]*>\s*(<figcaption[^>]*>\s*</figcaption>)?\s*</figure>", "", new)
        # srcset/sizes bei lokalen Bildern entfernen
        new = re.sub(r'\s(?:srcset|sizes)="[^"]*"', "", new)
        # Front-Matter-Bild, das fehlt
        new = re.sub(r'^image: "([^"]+)"\n', lambda m: "" if m.group(1) in missing else m.group(0), new, flags=re.M)
        # URLs ersetzen (längste zuerst)
        for u in sorted(mapping, key=len, reverse=True):
            new = new.replace(u, mapping[u])
        if new != t:
            with open(f, "w", encoding="utf-8") as fh:
                fh.write(new)
            changed += 1

    rest = sorted({u for t in (open(f, encoding="utf-8").read() for f in files) for u in URL_RE.findall(t)})
    report = os.path.join(ROOT, "docs", "bilder-import.md")
    with open(report, "w", encoding="utf-8") as r:
        r.write("# Bericht: Bilder-Import aus WordPress\n\n")
        r.write(f"- Lokal gespeicherte Dateien: **{len(used_names)}** in `assets/uploads/`\n")
        r.write(f"- Größe vorher (Originale): {total_in/1e6:.0f} MB, nachher: **{total_out/1e6:.0f} MB**\n")
        r.write(f"- Geänderte Beiträge: {changed}\n")
        r.write(f"- Schon auf dem alten Server fehlende Bilder (entfernt): **{len(missing)}**\n\n")
        if missing:
            r.write("## Fehlende Bilder (404 auf www.startupdorf.de)\n\n")
            for u in sorted(missing):
                r.write(f"- {u}\n")
        if rest:
            r.write("\n## Weiterhin auf www.startupdorf.de verlinkt\n\n")
            for u in rest:
                r.write(f"- {u}\n")
    print(f"{len(used_names)} Dateien, {total_in/1e6:.0f} MB → {total_out/1e6:.0f} MB, "
          f"{len(missing)} fehlend, {changed} Beiträge geändert, {len(rest)} Rest-Verweise", file=sys.stderr)


if __name__ == "__main__":
    main()
