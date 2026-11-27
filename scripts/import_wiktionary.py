#!/usr/bin/env python3

import json
import re
from datetime import date
from pathlib import Path

import requests

API_URL = "https://pl.wiktionary.org/w/api.php"
PAGE_TITLE = "Indeks:Włoski - Najpopularniejsze słowa"

ROOT = Path(__file__).resolve().parent.parent
WORDS_DIR = ROOT / "words"

WORDS_DIR.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": "italian-polish-dictionary/1.0"
}


def get_wikitext():
    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "titles": PAGE_TITLE,
        "format": "json",
        "formatversion": "2"
    }

    response = requests.get(
        API_URL,
        params=params,
        headers=HEADERS,
        timeout=60,
    )

    response.raise_for_status()

    data = response.json()

    pages = data["query"]["pages"]

    if not pages:
        raise RuntimeError("No page returned")

    return pages[0]["revisions"][0]["content"]


def extract_words(wikitext):
    """
    Wyciąga wszystkie [[hasła]] z indeksu.
    """

    matches = re.findall(r"\[\[([^\]|#]+)", wikitext)

    blacklist = {
        "Wikisłownik",
        "Wikipedia",
        "Pomoc",
        "Kategoria",
        "Kategorie",
        "Strona główna",
        "Indeks",
    }

    words = []
    seen = set()

    for item in matches:

        word = item.strip()

        if ":" in word:
            continue

        if word in blacklist:
            continue

        if len(word) < 2:
            continue

        if not re.match(
            r"^[A-Za-zÀ-ÿ' -]+$",
            word
        ):
            continue

        if word not in seen:
            seen.add(word)
            words.append(word)

    return words


def build_record(word, rank):

    today = date.today().isoformat()

    return {
        "id": f"it-{word}",
        "lemma": word,
        "language": "it",
        "frequency_rank": rank,
        "cefr": "unknown",
        "part_of_speech": "",
        "senses": [
            {
                "translations": [],
                "examples": []
            }
        ],
        "metadata": {
            "source": "pl.wiktionary.org",
            "created": today,
            "updated": today
        }
    }


def create_files(words):

    created = 0
    skipped = 0

    for rank, word in enumerate(words, start=1):

        filename = WORDS_DIR / f"{word}.json"

        if filename.exists():
            skipped += 1
            continue

        data = build_record(word, rank)

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2
            )

        created += 1

    return created, skipped


def main():

    print("Downloading index via MediaWiki API...")

    wikitext = get_wikitext()

    words = extract_words(wikitext)

    print(f"Found {len(words)} words")

    print("First 20 entries:")

    for word in words[:20]:
        print(f" - {word}")

    created, skipped = create_files(words)

    print(f"Created: {created}")
    print(f"Skipped: {skipped}")


if __name__ == "__main__":
    main()
