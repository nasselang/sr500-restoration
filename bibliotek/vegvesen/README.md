# Vegvesen-oppslag

Struktur for lagrede kjøretøyoppslag fra Vegvesenets AKF API.

## Konvensjon

Vi lagrer oppslag slik:

```text
bibliotek/vegvesen/<kjoretoytype>/<merke>/<modell>/<kjennemerke>.json
```

Eksempel:

```text
bibliotek/vegvesen/motorsykkel/yamaha/sr500-2j4/BB5092.json
```

## Navngiving

- `kjoretoytype`: enkel mappeform, f.eks. `motorsykkel`, `personbil`, `varebil`
- `merke`: små bokstaver, f.eks. `yamaha`
- `modell`: forenklet modellnavn, f.eks. `sr500-2j4`
- filnavn: kjennemerke uten mellomrom hvis mulig, men her beholdes vanlig regnr-format uten mellomrom i filnavnet

## Indeks

Alle strukturerte lagrede kjøretøy samles også i:

```text
bibliotek/vegvesen/index.json
```

`vegvesen_lookup.py` oppdaterer denne automatisk når et nytt oppslag lagres.

## Kilde

Dataene kommer fra:
- endpoint: `GET /enkeltoppslag/kjoretoydata`
- auth: `SVV-Authorization: Apikey <VEGVESEN_API_KEY>`
