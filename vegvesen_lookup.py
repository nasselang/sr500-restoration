#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
import unicodedata
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_URL = "https://akfell-datautlevering.atlas.vegvesen.no"
ENDPOINT = "/enkeltoppslag/kjoretoydata"
ENV_KEY = "VEGVESEN_API_KEY"
DEFAULT_HEADER_NAME = "SVV-Authorization"
COMMON_HEADER_NAMES = [
    "SVV-Authorization",
    "x-api-key",
    "X-API-Key",
    "Ocp-Apim-Subscription-Key",
    "Authorization",
]
SCRIPT_DIR = Path(__file__).resolve().parent
LIBRARY_ROOT = SCRIPT_DIR / "bibliotek" / "vegvesen"
INDEX_PATH = LIBRARY_ROOT / "index.json"


def load_env_file() -> None:
    env_path = SCRIPT_DIR / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)



def get_api_key(cli_value: str | None) -> str:
    if cli_value:
        return cli_value
    load_env_file()
    value = os.environ.get(ENV_KEY)
    if value:
        return value
    print(
        f"Mangler API-nøkkel. Sett {ENV_KEY} eller legg den i en .env-fil ved siden av scriptet.",
        file=sys.stderr,
    )
    sys.exit(2)



def build_url(kjennemerke: str | None, understellsnummer: str | None) -> str:
    params = {}
    if kjennemerke:
        params["kjennemerke"] = kjennemerke
    if understellsnummer:
        params["understellsnummer"] = understellsnummer

    if not params:
        print("Du må oppgi enten --kjennemerke eller --understellsnummer.", file=sys.stderr)
        sys.exit(2)

    return f"{BASE_URL}{ENDPOINT}?{urlencode(params)}"



def format_header_value(api_key: str, header_name: str) -> str:
    if header_name == "SVV-Authorization":
        return f"Apikey {api_key}"
    if header_name.lower() == "authorization":
        return f"Bearer {api_key}"
    return api_key



def fetch(url: str, api_key: str, header_name: str) -> object:
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            header_name: format_header_value(api_key, header_name),
        },
        method="GET",
    )
    with urlopen(request, timeout=20) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        data = response.read().decode(charset)
        return json.loads(data)



def try_header_names(url: str, api_key: str, header_names: list[str], compact: bool) -> int:
    failures: list[tuple[str, str]] = []

    for header_name in header_names:
        try:
            result = fetch(url, api_key, header_name)
            print(f"Fungerte med header: {header_name}", file=sys.stderr)
            if compact:
                print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
            else:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        except HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            failures.append((header_name, f"HTTP {e.code}: {body}"))
        except URLError as e:
            failures.append((header_name, f"Nettverksfeil: {e}"))
        except json.JSONDecodeError as e:
            failures.append((header_name, f"Ugyldig JSON: {e}"))

    print("Ingen av de vanlige headernavnene fungerte.", file=sys.stderr)
    for header_name, message in failures:
        print(f"- {header_name}: {message}", file=sys.stderr)
    return 1



def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "ukjent"



def model_slug(value: str) -> str:
    tokens = re.findall(r"[A-Za-z0-9]+", value.lower())
    if len(tokens) >= 2 and tokens[0].isalpha() and tokens[1].isdigit():
        tokens = [tokens[0] + tokens[1]] + tokens[2:]
    return "-".join(tokens) or "ukjent-modell"



def normalized_registration(value: str) -> str:
    return "".join(ch for ch in value.upper() if ch.isalnum())



def choose_vehicle_type(label: str) -> str:
    lowered = label.lower()
    mapping = [
        ("motorsykkel", "motorsykkel"),
        ("personbil", "personbil"),
        ("varebil", "varebil"),
        ("lastebil", "lastebil"),
        ("tilhenger", "tilhenger"),
        ("traktor", "traktor"),
        ("moped", "moped"),
        ("buss", "buss"),
    ]
    for needle, slug in mapping:
        if needle in lowered:
            return slug
    return slugify(label)



def extract_vehicle_record(result: object) -> dict:
    if not isinstance(result, dict):
        raise ValueError("Uventet responsformat fra API-et.")
    vehicles = result.get("kjoretoydataListe") or []
    if not vehicles:
        raise ValueError("Ingen kjøretøy funnet i responsen.")
    first = vehicles[0]
    if not isinstance(first, dict):
        raise ValueError("Uventet kjøretøyformat i responsen.")
    return first



def extract_metadata(vehicle: dict) -> dict[str, str]:
    identity = vehicle.get("kjoretoyId", {})
    teknisk = vehicle.get("godkjenning", {}).get("tekniskGodkjenning", {})
    klass = teknisk.get("kjoretoyklassifisering", {})
    tekniske_data = teknisk.get("tekniskeData", {})
    generelt = tekniske_data.get("generelt", {})

    reg_display = identity.get("kjennemerke") or ""
    if not reg_display:
        kjennemerker = vehicle.get("kjennemerke") or []
        if kjennemerker and isinstance(kjennemerker[0], dict):
            reg_display = kjennemerker[0].get("kjennemerke") or "UKJENT"
    reg_clean = normalized_registration(reg_display or "UKJENT")

    brand = "Ukjent"
    merker = generelt.get("merke") or []
    if merker and isinstance(merker[0], dict):
        brand = merker[0].get("merke") or brand

    handelsbetegnelse = (generelt.get("handelsbetegnelse") or [None])[0]
    typebetegnelse = generelt.get("typebetegnelse")
    model = handelsbetegnelse or typebetegnelse or "Ukjent modell"
    if typebetegnelse and typebetegnelse.lower() not in model.lower():
        model = f"{model} {typebetegnelse}"

    vehicle_type_label = (
        klass.get("tekniskKode", {}).get("kodeNavn")
        or klass.get("beskrivelse")
        or "Ukjent kjøretøytype"
    )

    return {
        "reg_display": reg_display or reg_clean,
        "reg_clean": reg_clean,
        "understellsnummer": identity.get("understellsnummer") or "",
        "brand": brand,
        "brand_slug": slugify(brand),
        "model": model,
        "model_slug": model_slug(model),
        "vehicle_type": vehicle_type_label,
        "vehicle_type_slug": choose_vehicle_type(vehicle_type_label),
    }



def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")



def save_result(result: object) -> Path:
    vehicle = extract_vehicle_record(result)
    meta = extract_metadata(vehicle)
    target = (
        LIBRARY_ROOT
        / meta["vehicle_type_slug"]
        / meta["brand_slug"]
        / meta["model_slug"]
        / f"{meta['reg_clean']}.json"
    )
    write_json(target, result)
    rebuild_index()
    return target



def summarize_vehicle_file(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    vehicle = extract_vehicle_record(data)
    meta = extract_metadata(vehicle)
    teknisk = vehicle.get("godkjenning", {}).get("tekniskGodkjenning", {}).get("tekniskeData", {})
    generelt = teknisk.get("generelt", {})
    motor = ((teknisk.get("motorOgDrivverk") or {}).get("motor") or [{}])[0]
    drivstoff = ((motor.get("drivstoff") or [{}])[0].get("drivstoffKode") or {}).get("kodeNavn")
    registrering = vehicle.get("registrering", {})

    return {
        "kjennemerke": meta["reg_clean"],
        "kjennemerkeVisning": meta["reg_display"],
        "understellsnummer": meta["understellsnummer"],
        "kjoretoytype": meta["vehicle_type"],
        "merke": meta["brand"],
        "modell": meta["model"],
        "registreringsstatus": (registrering.get("registreringsstatus") or {}).get("kodeBeskrivelse"),
        "forstegangsregistrertNorge": (vehicle.get("forstegangsregistrering") or {}).get("registrertForstegangNorgeDato"),
        "handelsbetegnelse": (generelt.get("handelsbetegnelse") or [None])[0],
        "typebetegnelse": generelt.get("typebetegnelse"),
        "slagvolum": motor.get("slagvolum"),
        "effektKw": ((motor.get("drivstoff") or [{}])[0].get("maksNettoEffekt")),
        "drivstoff": drivstoff,
        "relativePath": path.relative_to(LIBRARY_ROOT).as_posix(),
    }



def rebuild_index() -> None:
    LIBRARY_ROOT.mkdir(parents=True, exist_ok=True)
    vehicles = []
    for path in sorted(LIBRARY_ROOT.rglob("*.json")):
        if path == INDEX_PATH:
            continue
        relative_parts = path.relative_to(LIBRARY_ROOT).parts
        if len(relative_parts) < 4:
            continue
        try:
            vehicles.append(summarize_vehicle_file(path))
        except Exception as exc:
            vehicles.append(
                {
                    "relativePath": path.relative_to(LIBRARY_ROOT).as_posix(),
                    "error": f"Klarte ikke lese fil: {exc}",
                }
            )
    vehicles.sort(key=lambda item: item.get("kjennemerke", ""))
    write_json(INDEX_PATH, {"count": len(vehicles), "vehicles": vehicles})



def main() -> int:
    parser = argparse.ArgumentParser(
        description="Enkeltoppslag mot Vegvesenets API basert på kjennemerke eller understellsnummer."
    )
    parser.add_argument(
        "oppslag",
        nargs="?",
        help="Kortform: oppgi kjennemerke direkte, f.eks. 'NU1537'.",
    )
    parser.add_argument("--kjennemerke", help="Kjøretøyets kjennemerke")
    parser.add_argument("--understellsnummer", help="Kjøretøyets understellsnummer")
    parser.add_argument(
        "--api-key",
        help=f"API-nøkkel. Hvis utelatt brukes miljøvariabelen {ENV_KEY}.",
    )
    parser.add_argument(
        "--header-name",
        default=DEFAULT_HEADER_NAME,
        help=f"Headernavn for API-nøkkel. Standard er {DEFAULT_HEADER_NAME}.",
    )
    parser.add_argument(
        "--auto-header",
        action="store_true",
        help="Prøv vanlige headernavn automatisk og stopp på første som virker.",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Ikke lagre oppslaget automatisk i biblioteket.",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Skriv JSON på én linje i stedet for pen formattering.",
    )
    args = parser.parse_args()

    if args.oppslag and not args.kjennemerke and not args.understellsnummer:
        args.kjennemerke = args.oppslag

    api_key = get_api_key(args.api_key)
    url = build_url(args.kjennemerke, args.understellsnummer)

    if args.auto_header:
        return try_header_names(url, api_key, COMMON_HEADER_NAMES, args.compact)

    try:
        result = fetch(url, api_key, args.header_name)
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP-feil {e.code}: {body}", file=sys.stderr)
        return 1
    except URLError as e:
        print(f"Nettverksfeil: {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Klarte ikke lese JSON-respons: {e}", file=sys.stderr)
        return 1

    if not args.no_save:
        try:
            saved_path = save_result(result)
            print(f"Lagret til {saved_path.relative_to(SCRIPT_DIR)}", file=sys.stderr)
        except Exception as e:
            print(f"Advarsel: klarte ikke lagre i biblioteket: {e}", file=sys.stderr)

    if args.compact:
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
