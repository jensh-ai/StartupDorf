# CLAUDE.md – StartupDorf e.V. Webseite

Neue Webseite für StartupDorf e.V. (Gründer-Community Düsseldorf, seit 2013). Sie löst die WordPress-Seite www.startupdorf.de ab.
Jekyll 4, gebaut per GitHub Actions, veröffentlicht auf GitHub Pages.
Vorschau: https://jensh-ai.github.io/StartupDorf/ (`baseurl` /StartupDorf). Später kommt die eigene Domain www.startupdorf.de dazu (`baseurl` leer).

## Rolle & Kommunikation
- Sprache mit dem Nutzer: **Deutsch**. Die Seite ist zunächst deutsch, Englisch folgt später.
- Du bist **Berater für Gestaltung und SEO**. Wünsche kritisch hinterfragen und Alternativen begründen. Bei echten Zielkonflikten nachfragen statt raten.
- Ziele der Seite: (1) **die nächsten Events prominent zeigen**, (2) Auffindbarkeit/SEO, (3) **Sponsoren und Gastgeber gewinnen**, denen ein Mehrwert gezeigt wird, (4) News und Blog für wiederkehrende Besucher.
- Das bestehende Erscheinungsbild (seit 2013) bleibt wiedererkennbar: Rot `#c0131e`, Dunkelrot `#920e17`, Schwarz `#181818`, Schriften Nunito Sans (Text) und Open Sans (Überschriften), Logo mit dem Rheinturm.

## Workflow
- **Direkt auf `main` committen und pushen.** So hat es der Nutzer entschieden, solange noch viel iteriert wird. Jeder Push auf `main` geht live in die Vorschau.
- Vor jedem Push: `bundle exec jekyll build` muss fehlerfrei laufen. Bei Pfad- oder Link-Änderungen zusätzlich mit `--baseurl /StartupDorf` bauen und die internen Links prüfen (Beispielskript im Abschnitt „Bekannte Fallstricke“).
- Visuelle Änderungen mit Playwright prüfen, Desktop 1366 px und iPhone 13. Lokal servieren: `cd _site && python3 -m http.server 4000`. Beim Neubauen wird `_site` ersetzt, danach den Server neu starten. Bilder laden erst beim Scrollen (`loading=lazy`): vor einem Screenshot der ganzen Seite durchscrollen.
- Der Deploy-Workflow `.github/workflows/pages.yml` läuft bei jedem Push auf `main`, täglich um 04:17 UTC (damit vergangene Events ins Archiv rutschen) und manuell. Die Umgebung `github-pages` lässt nur `main` veröffentlichen.

## Befehle
```bash
bundle install                          # Gems landen in vendor/bundle
bundle exec jekyll serve                # lokal: http://localhost:4000
bundle exec jekyll build --baseurl /StartupDorf -d /tmp/site-bu   # Vorschau-Build testen
python3 tools/import_wordpress.py [--from-dir DIR]   # Beiträge neu aus der WP-REST-API (überschreibt _posts/)
python3 tools/localize_images.py [--cache DIR]       # danach: Bilder lokal holen, WebP, Links umschreiben
```
Die beiden Import-Skripte zusammen sind deterministisch. Aber: Ein erneuter Import überschreibt auch alle Änderungen, die von Hand an `_posts/*.html` gemacht wurden.

## Struktur
| Pfad | Inhalt |
|---|---|
| `_config.yml` | Seiten- und Vereinsdaten (`org:`), `noindex: true` (Entwurf!), `future: true`, Collections |
| `_events/JJJJ-MM-TT-name.md` | Events. Felder angelehnt an die Eventbrite-API (siehe README). `start`/`end` **immer als String in Anführungszeichen** |
| `_posts/*.html` | 156 importierte WordPress-Beiträge (HTML, `render_with_liquid: false`, `lang: de\|en`, `wp_id`, `wp_url`). Neue Beiträge als `.md` |
| `_data/` | `navigation`, `formate` (Format-Schlüssel für Events), `partner` (Entwurf, aus Blogbeiträgen abgeleitet), `kennzahlen` (Platzhalter), `stimmen` |
| `_includes/` | `head` (SEO, JSON-LD), `header`, `footer`, `event-card`, `post-card`, `events-split` (teilt Events in `upcoming`/`past`), `datum` (deutsche Datumsformate), `jsonld-*` |
| `_layouts/` | `default`, `page`, `post`, `event` |
| `_plugins/baseurl_uploads.rb` | Setzt die baseurl vor `/assets/uploads/` in gerendertem HTML (nur nötig, solange die Seite unter /StartupDorf läuft) |
| `index.html`, `events/`, `events.ics`, `blog/`, `formate/`, `unterstuetzen.md`, `mitmachen.md`, `ueber-uns.md`, `impressum.md`, `datenschutz.md`, `404.html` | Seiten |
| `assets/css/main.scss` | Gesamtes Design, Farbwerte als CSS-Variablen in `:root` |
| `assets/fonts/` | Schriften selbst gehostet (kein Google Fonts, wegen DSGVO) |
| `assets/uploads/JJJJ/MM/` | 523 Blogbilder als WebP (max. 1600 px, ca. 53 MB). Die Originale gehören **nicht** ins Repo |
| `docs/MIGRATION.md` | **Offene Aufgaben**, zuerst lesen |
| `docs/bilder-import.md` | Bericht zum Bilder-Import (fehlende Bilder, Rest-Verweise auf den alten Server) |

## Getroffene Entscheidungen
- **Blog-Permalinks = alte WordPress-URLs** (`/<slug>/`), damit Rankings und Backlinks erhalten bleiben. Ausnahme: Slugs mit Umlaut wurden zu ASCII mit `redirect_from` auf die alte URL.
- **Events aus Eventbrite** werden nicht per iframe/Widget eingebunden: schlecht für SEO, setzt Cookies. Stattdessen eigene Eventseiten mit `schema.org/Event` und dem ICS-Feed `/events.ics`. Die Anmeldung verlinkt auf Eventbrite. Ob Events künftig automatisch (Eventbrite-API) oder von Hand gepflegt werden, ist **noch offen**.
- Eventbrite zeigt **vergangene Events nicht öffentlich**. Die vier vergangenen Events stammen aus Blog-Rückblicken.
- **Keine Cookies, kein Tracking, keine Drittanbieter-Skripte** → kein Cookie-Banner nötig. YouTube-Einbettungen laufen über `youtube-nocookie.com`.
- **Tickets:** Ticketarten und Preise stehen auf Eventbrite. Eventseiten zeigen den Hinweis aus `tickets_hinweis` (`_config.yml`, pro Event überschreibbar). Im JSON-LD steht bewusst kein `price`.
- Formulare (Mitgliedschaft, Pitch-Bewerbung) sind vorerst `mailto:`-Links. Ein Formulardienst ist noch nicht entschieden.
- Ein CMS (z. B. Pages CMS oder Decap) kommt später. Der Nutzer arbeitet derzeit selbst mit GitHub.
- Kennzahlen: Stammtisch jeden ersten Mittwoch im Monat, 40–80 Gäste, über 140 Ausgaben, Grand Final 2026 mit 125 Tickets ausverkauft. **Weitere Zahlen liefert der Nutzer nach.**

## Bekannte Fallstricke
- `future: true` ist nötig, weil Events in der Zukunft liegen. Nebenwirkung: Beiträge mit Zukunftsdatum erscheinen sofort.
- Event-Permalink: `/events/:year-:month-:day-:title/`. Mit `:name` würde Jekyll das Datum entfernen, und Events mit gleichem Namen überschreiben sich gegenseitig.
- Event-Daten **in Anführungszeichen setzen**. Gemischte Date/Time-Typen lassen `sort` abbrechen. Nur-Datum (`"2026-09-02"`) ist erlaubt, im JSON-LD wird dann nur das Datum ausgegeben.
- Liquid `include` akzeptiert kein `var[0]`: vorher `assign x = var | first`.
- WordPress-HTML verwendet teils `href='…'` mit einfachen Anführungszeichen. Das baseurl-Plugin deckt beide Schreibweisen ab.
- Links in Markdown-Seiten immer mit `{{ '/pfad/' | relative_url }}` schreiben, sonst brechen sie unter /StartupDorf.
- `noindex: true` in `_config.yml` erst beim Livegang auf `false` setzen. Vorher droht Duplicate Content zur alten WordPress-Seite.

## Inhaltliche Quellen
- Alte Seite: https://www.startupdorf.de (WordPress-REST-API: `/wp-json/wp/v2/posts`, `/pages`, `/categories`)
- Eventbrite-Veranstalter: https://www.eventbrite.de/o/15406173560 (Abrufe per curl werden blockiert, eine einzelne Eventseite lädt aber, und deren `og:`- und `ld+json`-Daten sind brauchbar)
- Impressumsdaten stammen von der alten Seite (Stand 2023). Die Vereinsregister-Nummer fehlt noch.
