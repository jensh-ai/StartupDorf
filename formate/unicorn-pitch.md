---
title: Unicorn Pitch
kicker: Formate · Pitch-Wettbewerb
lead: Sechs Startups, fünf Minuten Pitch, fünf Minuten Fragen. Jury und Publikum entscheiden – die Besten ziehen ins Grand Final und kämpfen um den Titel „StartupDorf Unicorn of the Year“.
description: "Der Unicorn Pitch von StartupDorf e.V.: Pitch-Wettbewerb für Startups in Düsseldorf mit Vorrunden und Grand Final. Jetzt bewerben und vor Jury und Publikum pitchen."
---
{% include events-split.html %}
{%- assign naechste = upcoming | where: "format", "unicorn-pitch" %}
{%- assign letzte = past | where: "format", "unicorn-pitch" %}

## So funktioniert's

- **Vorrunden:** Zweimal im Jahr pitchen je sechs Startups – auf Deutsch oder Englisch, mit Pitch-Deck.
- **Zwei Gewinner pro Runde:** Jury und Publikum stimmen getrennt ab.
- **Grand Final:** Die Gewinner der Vorrunden treten im Frühjahr gegeneinander an. 2026 waren alle 125 Tickets lange vorher ausverkauft.

<div class="box" markdown="1">
**Ihr wollt pitchen?** Bewerbt euch mit eurem Startup für die nächste Vorrunde. [Jetzt bewerben](mailto:contact@startupdorf.de?subject=Bewerbung%20Unicorn%20Pitch)
</div>

{%- if naechste.size > 0 %}
## Nächste Termine
<div class="event-list">{% for e in naechste %}{% include event-card.html event=e %}{% endfor %}</div>
{%- endif %}

{%- if letzte.size > 0 %}
## Zuletzt
<div class="event-list">{% for e in letzte limit: 4 %}{% include event-card.html event=e past=true %}{% endfor %}</div>
{%- endif %}

## Partner

Der Unicorn Pitch wird möglich durch Partner wie HEUKING, NRW.BANK, Holvi, gradar und die WHU – Otto Beisheim School of Management. [Partner werden →]({{ '/unterstuetzen/#sponsoring' | relative_url }})
