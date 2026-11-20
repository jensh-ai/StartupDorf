# StartupDorf e.V. – Webseite

Neue Webseite von [StartupDorf e.V.](https://www.startupdorf.de), gebaut mit [Jekyll](https://jekyllrb.com) und veröffentlicht über GitHub Pages.

> **Status: Entwurf.** Die Seite ist per `noindex` vor Suchmaschinen versteckt, bis sie die WordPress-Seite ablöst. Offene Punkte stehen in [docs/MIGRATION.md](docs/MIGRATION.md).

## Lokal starten

Voraussetzung: Ruby 3.x und Bundler.

```bash
bundle install
bundle exec jekyll serve
```

Danach unter http://localhost:4000 öffnen. Änderungen werden automatisch neu gebaut.

## Inhalte pflegen

| Was | Wo | Hinweis |
|---|---|---|
| **Events** | `_events/JJJJ-MM-TT-name.md` | Eine Datei pro Event, Felder siehe unten. Vergangene Events wandern automatisch ins Archiv. |
| **Blogbeiträge** | `_posts/JJJJ-MM-TT-titel.md` | Markdown mit `title`, `description`, `image`, `categories`. Die URL ist `/<titel>/`. |
| **Formate** | `_data/formate.yml` und `formate/` | Kurztexte für Startseite, eigene Seiten für Stammtisch & Unicorn Pitch. |
| **Partner/Gastgeber** | `_data/partner.yml` | Erscheinen auf Startseite und `/unterstuetzen/`. |
| **Kennzahlen** | `_data/kennzahlen.yml` | Der rote Zahlen-Streifen auf der Startseite. |
| **Stimmen** | `_data/stimmen.yml` | Testimonials. |
| **Navigation** | `_data/navigation.yml` | |
| **Vereinsdaten** | `_config.yml` → `org:` | Adresse, E-Mail, Social Links – werden überall verwendet. |

### Event anlegen

Die Felder orientieren sich an der Eventbrite-API, damit ein späterer automatischer Import dieselbe Struktur befüllen kann.

```yaml
---
title: "Gründerstammtisch #144"
subtitle: "Optionaler Untertitel"
format: gruenderstammtisch        # Schlüssel aus _data/formate.yml
start: "2027-01-06T18:00:00+01:00" # oder nur "2027-01-06", wenn die Uhrzeit offen ist
end: "2027-01-06T22:00:00+01:00"
venue:
  name: Mindspace Grünstraße
  street: Grünstraße 15
  postal_code: "40212"
  city: Düsseldorf
  lat: 51.2211143                  # optional, für Karte & Google
  lng: 6.7809579
host: Mindspace Düsseldorf         # Gastgeber, wird auf der Eventseite gedankt
tickets_hinweis: "…"            # optional, sonst Standardtext aus _config.yml (bewusst ohne Preise)
tickets_url: https://www.eventbrite.de/e/...
image: /assets/img/event-144.jpg   # ca. 940×470 px
summary: "Ein Satz für Karten, Google und Kalender."
status: scheduled                  # oder cancelled
source: eventbrite
eventbrite_id: "..."
recap_url: /rueckblick-beitrag/    # optional: Link zum Blog-Rückblick
---
Beschreibung in Markdown.
```

Für jedes Event entstehen automatisch:

- eine eigene Seite unter `/events/JJJJ-MM-TT-name/` mit strukturierten Daten (`schema.org/Event`), damit Google das Event in der Suche anzeigen kann
- ein Eintrag im abonnierbaren Kalender `/events.ics`
- die Anzeige als „Nächstes Event“ auf der Startseite

## Hosting & Deployment

Gebaut wird mit **GitHub Actions**, veröffentlicht auf **GitHub Pages** (`.github/workflows/pages.yml`). So sind Plugins außerhalb der Pages-Whitelist möglich. Außerdem baut die Action die Seite **täglich** neu, damit vergangene Events von selbst ins Archiv rutschen.

Einmalig einrichten:

1. Im Repository unter **Settings → Pages → Build and deployment → Source** „**GitHub Actions**“ wählen.
2. Auf `main` pushen (oder den Workflow manuell starten). Die Seite erscheint unter `https://<owner>.github.io/<repo>/`.
3. **Eigene Domain** (erst beim Livegang): unter *Settings → Pages → Custom domain* `www.startupdorf.de` eintragen. Beim DNS-Anbieter einen `CNAME`-Eintrag `www → <owner>.github.io` und für die nackte Domain die vier `A`-Records von GitHub Pages setzen. Danach „Enforce HTTPS“ aktivieren und in `_config.yml` `noindex: false` setzen.

## Werkzeuge

- `tools/import_wordpress.py` importiert die Blogbeiträge erneut aus der WordPress-REST-API (`python3 tools/import_wordpress.py`). **Achtung:** Das überschreibt `_posts/`.
- `tools/localize_images.py` lädt danach alle Bilder und PDFs der Beiträge vom alten Server, verkleinert sie (WebP, max. 1600 px) und legt sie unter `assets/uploads/` ab (benötigt Pillow: `pip install Pillow`).
- `tools/rewrite_links.py` biegt danach Links in den Beiträgen von www.startupdorf.de auf die neue Seite um (Galerie-Links → WebP, Beitragslinks → lokal, alte Seiten → neue Seiten laut Zuordnung). Bericht: `docs/link-umschreibung.md`.
- `_plugins/baseurl_uploads.rb` sorgt dafür, dass die Bildpfade der Beiträge auch in der Vorschau unter `…github.io/StartupDorf/` funktionieren.

### Bilder in neuen Beiträgen

Bilder vor dem Hochladen verkleinern (max. 1600 px, WebP oder JPEG unter ca. 300 KB) und unter `assets/uploads/JJJJ/MM/` ablegen. Im Beitrag dann mit `![Beschreibung](/assets/uploads/JJJJ/MM/bild.webp)` einbinden. Die Bildbeschreibung (Alt-Text) hilft bei Barrierefreiheit und Google-Bildersuche.
