# Migration WordPress → Jekyll: offene Punkte

Stand: Entwurf vom November 2026. Abhaken, sobald erledigt.

## Vor dem Livegang (Pflicht)

### SEO: alte URLs erhalten
- [ ] **Alle URLs der alten Seite erfassen**: Sitemap (`/sitemap_index.xml`), Google Search Console (Seiten mit Klicks und Impressionen), Backlinks. Ergebnis als Liste in `docs/url-inventar.csv`.
- [ ] **301-Weiterleitungen** für alle Seiten einrichten, die es nicht mehr gibt, per `redirect_from` im Front Matter der neuen Seite (Plugin `jekyll-redirect-from` ist installiert). Bekannte Kandidaten:
  - `/about/` → `/ueber-uns/`, `/about/imprint/` → `/impressum/`, `/about/privacy/` → `/datenschutz/`
  - `/event-calendar/` → `/events/`
  - `/services/founders-night/` → `/formate/gruenderstammtisch/`
  - `/pitching/` → `/formate/unicorn-pitch/`, `/power-pitch/`, `/dorfschule/` → `/formate/`
  - `/mitgliedschaft/`, `/mitgliedschaften/`, `/services/for-startups/`, `/services/supporting-members/`, `/for-individual-supporter/`, `/mitgliedschaft-fur-*` → `/mitmachen/`
  - `/sponsors/` → `/unterstuetzen/`, `/blog/latest-news/` → `/blog/`
  - `/de/...` (Sprachversionen), `/category/...`, `/tag/...`, `/author/...`, `/page/N/`
  - `/startup-wall/`, `/listing/...` → Entscheidung offen (siehe unten)
  - Hinweis: GitHub Pages kann nur per HTML/JS weiterleiten, nicht mit echtem HTTP-301. Google wertet das in der Regel wie eine Weiterleitung. Wer echte 301 braucht, schaltet z. B. Cloudflare davor.
- [x] Blogbeiträge behalten ihre alten Permalinks (`/<slug>/`) und brauchen keine Weiterleitung.
- [ ] Interne Links in Blogbeiträgen zeigen noch absolut auf `https://www.startupdorf.de/...`. Nach dem Umzug prüfen, ob die Ziele existieren.

### Bilder der Blogbeiträge
- [ ] Bilder in `_posts/` werden noch von `www.startupdorf.de/wp-content/uploads/` geladen. **Bevor WordPress abgeschaltet wird**, alle Bilder herunterladen (z. B. nach `assets/uploads/`) und die URLs ersetzen. Sonst sind alle Bilder weg.
- [ ] Dabei Bilder verkleinern (WebP, max. 1600 px), das hilft bei Ladezeit und Core Web Vitals.

### Recht
- [ ] Impressum prüfen: Vorstand aktuell? **Vereinsregister-Nummer fehlt** (für e.V. Pflicht).
- [ ] Datenschutzerklärung rechtlich prüfen lassen (Entwurf liegt vor).
- [ ] Rechte an Fotos klären (Fotograf z. B. manorlux.de), Bildnachweise ergänzen.
- [ ] Zitate in `_data/stimmen.yml` freigeben lassen.

### Livegang
- [ ] `_config.yml`: `noindex: false`
- [ ] DNS umstellen, Custom Domain und HTTPS in GitHub Pages aktivieren
- [ ] Google Search Console: neue Sitemap `https://www.startupdorf.de/sitemap.xml` einreichen, Weiterleitungen überwachen
- [ ] Google-Unternehmensprofil (Google Business Profile) für StartupDorf e.V. anlegen oder aktualisieren und auf die neue Seite verlinken

## Inhalte, die noch fehlen

- [ ] **Kennzahlen** für Sponsoren und Gastgeber (`_data/kennzahlen.yml`): Teilnehmer pro Event, Mitgliederzahl, Follower und Reichweite je Kanal, Newsletter-Abonnenten. Ohne Zahlen überzeugt die Sponsorenseite nicht.
- [ ] **Partnerliste** (`_data/partner.yml`) vom Vorstand bestätigen lassen. Sie ist aus Blogbeiträgen 2025/26 abgeleitet. Logos ergänzen (freigegeben, möglichst SVG).
- [ ] Sponsoring-Pakete konkretisieren (Leistungen, ggf. Preise) oder bewusst „auf Anfrage“ lassen.
- [ ] Ein **Media-Kit (PDF)** für Gastgeber und Sponsoren zum Download.
- [ ] Vergangene Events: bisher nur 4 Events aus Blog-Rückblicken (Eventbrite zeigt vergangene Events nicht öffentlich an). Weitere Stammtische nachtragen, wenn gewünscht.
- [ ] Team-/Vorstandsseite mit Fotos (Vertrauen und E-E-A-T für Google).
- [ ] Startup-Wall / Mitgliederverzeichnis: gibt es dafür noch Bedarf? In WordPress lief das über ein Plugin, statisch ginge es als `_data/startups.yml`.

## Formulare

Die WordPress-Formulare (Mitgliedsantrag, Unicorn-Pitch-Bewerbung, Newsletter) gibt es auf einer statischen Seite nicht. Im Entwurf führen alle Buttons zu `mailto:`. Optionen:
- Externer Formulardienst (z. B. Tally oder Formspree, auf DSGVO-Konformität achten), oder
- Bestehenden Newsletter-Anbieter einbinden, oder
- bei E-Mail bleiben (am einfachsten, aber mehr Handarbeit).

## Später

- [ ] **Events automatisch von Eventbrite** übernehmen: geplanter GitHub-Action-Job oder Scheduled Task, der über die Eventbrite-API (`/v3/organizers/15406173560/events/`, privater Token als Secret) Dateien in `_events/` schreibt. Die Feldstruktur ist schon darauf ausgelegt.
- [ ] **CMS** für Redakteure ohne Git (z. B. Pages CMS oder Decap CMS): eine Konfiguration für `_events`, `_posts` und `_data` genügt.
- [ ] **Englische Version**: `jekyll-polyglot` oder eigene `/en/`-Struktur mit `hreflang`. Ältere Beiträge sind schon mit `lang: en|de` markiert.
- [ ] Kategorie-Archive im Blog (z. B. alle Unicorn-Pitch-Rückblicke).
- [ ] Logo als SVG (aktuell PNG mit 246×100 px, auf großen Bildschirmen leicht unscharf).
