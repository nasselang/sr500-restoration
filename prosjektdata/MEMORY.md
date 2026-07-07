# MEMORY.md – Langtidsminne

**Dette er din hovedfil for langtidsminne i OpenClaw.**
Her lagrer vi viktige punkter, permanente referanser og kontekst som skal vare over flere sesjoner.

---

## Gjenopprettet langtidsminne (fra daglige minner)

- **SR500-prosjektet** er konsolidert til `/home/johnny/.openclaw/workspace/projects/sr500-restoration/`:
  - `data/` — deler, CSV-er, bilder, notater (pr subsystem)
    - Hvert subsystem har eget bilde i sin mappe (f.eks. `data/carburetor/carburetor.jpg`, `data/frame/frame.jpg`)
    - `data/images/SR500prosjekt` → symlink til OneDrive: `/mnt/c/Users/nasse/OneDrive/Bilder/SR500prosjekt`
  - `reference/` — PDF-kataloger, delelister
  - `bibliotek/` — vegvesen/registreringsdata
  - `memory/` — historiske minnefiler om prosjektet
- **SR500-agenten** (`id: sr500`) har workspace satt til prosjektmappa og agentfiler (SOUL.md, IDENTITY.md, USER.md, TOOLS.md) fylt ut.
- **Shoppinglisten**: `projects/sr500-restoration/data/notes/shopping_list.md`
- **Leverandøroversikt**: `data/notes/leverandoroversikt.md` — komplett oversikt over alle leverandører for SR500-prosjektet: OEM-deler (CMSNL, MegaZip, KEDO), ettermarked (Yambits, Webike, MotoLanna), norske forhandlere (Skruvat, Autodoc, AGM, Højstyling, Ravns Garage), elektronikk (motogadget, Vape), og pulverlakkering (Oslopulverlakk ⭐).
- **Pulverlakkering**: Oslopulverlakk (Rælingen) er foretrukket leverandør for ramme-pulverlakkering.
- **Nøkkeldata**: `projects/sr500-restoration/data/notes/project_facts.md`
- **Kjente problemer**:
  - Manglet MEMORY.md før denne gjenopprettingen.
  - Vedlegg til Telegram har hatt problemer, spesielt på bilder.

---

- **Google Calendar integrasjon**: gog er ferdig konfigurert, og passordfrase ligger i `openclaw.json`. gog fungerer fra terminalen.

---

- **Automatisk oppslag av registreringsnummer:** Når Johnny ber om oppslag på et registreringsnummer, kjør `./regnr <REGNR>` (fra workspace rota eller `projects/sr500-restoration/`). Lagrer resultatet i `bibliotek/vegvesen/`.

---

- **Uleste Gmail-eposter:**
  Seneste uleste e-poster inkluderte sikkerhetsvarsler fra Google og flere promoteringer (Spotify, Pinterest og HX Expeditions). Kan sjekkes på nytt via `gog gmail search "is:unread"` om nødvendig.

---

- **Forgasser og deler:** Når Johnny spør om et delenummer relatert til bildet carburetor.jpg, bruk informasjonen i filen carburetor_parts.csv for å finne detaljer.

---

- **Nyttig lenke lagret:** [Yambits Yamaha SR500 deler](https://yambits.co.uk/parts_for_yamaha_sr500.html) (kan brukes senere for SR500-relaterte deler).

---

## Prosjektstatus

- **2026-05-31:** Sandblåser mottatt! Planen er å blåse deler først, ramma kommer etterpå.
- **2026-06-08:** Sandblåser i drift! Styrekrone sandblåst med bra resultat.
- **2026-06-19:** Ramme + svingarm tilbake fra Oslopulverlakk ✅ kr 5 250. Tank levert for lakkering.
- **2026-06-22:** CMSNL flensbolt sendt (UPS sporing). eBay bestillinger: styre, forskjerm, verkstedhåndbok.
- **2026-06-23:** Motogadget bestilt! mo.unit blue + mo.button + switches — €670 totalt.
- **2026-06-26:** Svinghjulsavdrager (27×1mm LH) bestilt fra Thansen — kr 119.
- **2026-06-26:** VAPE Ignition bestilt fra TOLA-Tools (#202652798) — €533,79 ~kr 6 200. PayPal ✅
- **2026-06-27:** Lager+simring-sett forhjul bestilt fra Online MC (#89847) — kr 530
- **2026-07-02:** CMSNL flensbolt, Motogadget-pakke, Online MC forhjul-sett og Thansen svinghjulsavdrager ✅ **Mottatt**
- **2026-07-03:** ✅ **Tank hentet fra lakkering — sort finish!** Bilder lagret i `data/tank/`.

## Totalt investert hittil
- ~kr 27 923

## AliExpress
- Flensbolt M8×12mm (95811-08012-00) ×5 bestilt 05.07 — under kr 100. Bra alternativ for standardbolter til en brøkdel av OEM-pris.

- **Publiseringsrutine:** Alltid vis utkast til Johnny før publisering til GitHub Pages. Aldri push uten godkjenning. Blogg: https://nasselang.github.io/sr500-restoration/
