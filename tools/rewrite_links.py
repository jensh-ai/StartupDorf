#!/usr/bin/env python3
"""Biegt Links in den Blogbeiträgen von www.startupdorf.de auf die neue Seite um.

Läuft nach tools/localize_images.py:
  python3 tools/rewrite_links.py

- Link um ein lokales Bild (WordPress-„Anhangseite“) -> direkt auf die WebP-Datei
- Link auf einen anderen Beitrag (auch /de/<slug>/) -> /<slug>/
- Link auf eine alte Seite -> neue Seite laut ZUORDNUNG
- Alles andere bleibt und landet im Bericht docs/link-umschreibung.md

Idempotent: Ein zweiter Lauf ändert nichts.
"""
import collections
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS = os.path.join(ROOT, "_posts")
REPORT = os.path.join(ROOT, "docs", "link-umschreibung.md")

# Alte WordPress-Seiten -> neue Seiten. Auch Grundlage für spätere redirect_from-Weiterleitungen.
ZUORDNUNG = {
    "/": "/",
    "/pitching/": "/formate/unicorn-pitch/",
    "/de/pitching/": "/formate/unicorn-pitch/",
    "/de/everything-you-should-know-about-the-unicorn-pitch/": "/formate/unicorn-pitch/",
    "/everything-you-should-know-about-the-unicorn-pitch/": "/formate/unicorn-pitch/",
    "/power-pitch/": "/formate/#power-pitch",
    "/de/power-pitch/": "/formate/#power-pitch",
    "/ninja-pitch/": "/formate/#power-pitch",
    "/dorfschule/": "/formate/#dorfschule",
    "/services/founders-night/": "/formate/gruenderstammtisch/",
    "/contact/": "/ueber-uns/#kontakt",
    "/services/contact/": "/ueber-uns/#kontakt",
    "/about/": "/ueber-uns/",
    "/about/faq/": "/ueber-uns/",
    "/about/locations/": "/ueber-uns/",
    "/about/startupdorf-highlights-history/": "/ueber-uns/",
    "/sponsors/": "/unterstuetzen/",
    "/supporting-membership/": "/unterstuetzen/#sponsoring",
    "/services/supporting-members/": "/unterstuetzen/#sponsoring",
    "/mitgliedschaft/": "/mitmachen/",
    "/mitgliedschaften/": "/mitmachen/",
    "/startup-become-a-member/": "/mitmachen/#startups",
    "/membership-types/": "/mitmachen/",
    "/membership-application/": "/mitmachen/",
    "/startup-membership-application/": "/mitmachen/#startups",
    "/services/for-startups/": "/mitmachen/#startups",
    "/calendar/": "/events/",
    "/event-calendar/": "/events/",
    "/blog/": "/blog/",
}

A_RE = re.compile(r"""<a\b([^>]*?)\bhref=(["'])(https?://(?:www\.)?startupdorf\.de(?:/[^"']*)?)\2([^>]*)>(.*?)</a>""", re.S | re.I)
IMG_RE = re.compile(r"""<img\b[^>]*\bsrc=["'](/assets/uploads/[^"']+)["']""", re.I)


def norm_path(url):
    path = re.sub(r"^https?://(?:www\.)?startupdorf\.de", "", url)
    path = path.split("#")[0].split("?")[0] or "/"
    last = path.rstrip("/").split("/")[-1]
    if not path.endswith("/") and "." not in last:
        path += "/"
    return path


def main():
    files = sorted(os.path.join(POSTS, f) for f in os.listdir(POSTS))
    permalinks = set()
    for f in files:
        m = re.search(r"^permalink: (\S+)", open(f, encoding="utf-8").read(), re.M)
        if m:
            permalinks.add(m.group(1))

    stats = collections.Counter()
    rest = collections.Counter()
    changed = 0
    for f in files:
        text = open(f, encoding="utf-8").read()

        def repl(m):
            pre, q, url, post, inner = m.groups()
            img = IMG_RE.search(inner)
            path = norm_path(url)
            target = None
            if img:
                target, kind = img.group(1), "Bild"
            elif path in permalinks:
                target, kind = path, "Beitrag"
            elif path.startswith("/de/") and path[3:] in permalinks:
                target, kind = path[3:], "Beitrag"
            elif path in ZUORDNUNG:
                target, kind = ZUORDNUNG[path], "Seite"
            if target is None:
                return m.group(0)
            stats[kind] += 1
            return f"<a{pre}href={q}{target}{q}{post}>{inner}</a>"

        # Mehrfach anwenden: Bei unsauberem WordPress-HTML (fehlendes </a>) verschluckt ein
        # Treffer den nächsten Link, der dann erst im folgenden Durchgang erkannt wird.
        new, prev = text, None
        while new != prev:
            prev = new
            new = A_RE.sub(repl, new)

        # Schon relative Links auf alte Seiten (z. B. href="/sponsors/") ebenfalls zuordnen
        def repl_rel(m):
            q, path = m.group(1), m.group(2)
            p = norm_path(path)
            if p in ZUORDNUNG and p not in permalinks and ZUORDNUNG[p] != p:
                stats["Seite"] += 1
                return f"href={q}{ZUORDNUNG[p]}{q}"
            return m.group(0)
        new = re.sub(r"""href=(["'])(/(?!/|assets/)[^"']*)\1""", repl_rel, new)
        if new != text:
            with open(f, "w", encoding="utf-8") as fh:
                fh.write(new)
            changed += 1
        # Verbleibende Links auf die alte Domain (unabhängig von der Verschachtelung zählen)
        for url in re.findall(r"""<a\b[^>]*\bhref=["'](https?://(?:www\.)?startupdorf\.de(?:/[^"']*)?)["']""", new, re.I):
            if "/wp-content/" not in url:
                rest[url] += 1
                stats["unverändert"] += 1

    with open(REPORT, "w", encoding="utf-8") as r:
        r.write("# Bericht: Links in Blogbeiträgen umgeschrieben\n\n")
        r.write("Erzeugt von `tools/rewrite_links.py`. Zahlen stammen aus dem letzten Lauf auf frisch importierten Beiträgen.\n\n")
        r.write(f"- Bild-Links (Anhangseite → WebP): **{stats['Bild']}**\n")
        r.write(f"- Links auf andere Beiträge: **{stats['Beitrag']}**\n")
        r.write(f"- Links auf alte Seiten (Zuordnung): **{stats['Seite']}**\n")
        r.write(f"- Weiterhin auf www.startupdorf.de: **{stats['unverändert']}** (Liste unten)\n\n")
        if rest:
            r.write("## Verbleibende Links auf www.startupdorf.de\n\n")
            r.write("Noch ohne Gegenstück auf der neuen Seite, z. B. die alte Startup-Wall (`/listing/…`). "
                    "Entscheidung zusammen mit den Weiterleitungen (siehe MIGRATION.md).\n\n")
            for url, n in sorted(rest.items()):
                r.write(f"- {url}" + (f" ({n}×)" if n > 1 else "") + "\n")
    print(f"Bild {stats['Bild']}, Beitrag {stats['Beitrag']}, Seite {stats['Seite']}, "
          f"unverändert {stats['unverändert']}, {changed} Dateien geändert")


if __name__ == "__main__":
    main()
