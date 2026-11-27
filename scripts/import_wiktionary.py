#!/usr/bin/env python3

import json
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

INDEX_URL = (
    "https://pl.wiktionary.org/wiki/"
    "Indeks:W%C5%82oski_-_Najpopularniejsze_s%C5%82owa"
)

ROOT = Path(__file__).resolve().parent.parent
WORDS_DIR = ROOT / "words"

WORDS_DIR.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": (
        "italian-polish-dictionary/1.0 "
        "(GitHub project)"
    )
}


def slug_to_id(word):
    return f"it-{word}"


def build_skeleton(word, rank):

    return {
        "id": slug_to_id(word),
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
            "created": "2026-11-27",
            "updated": "2026-11-27"
        }
    }


def fetch_index():

    response = requests.get(
        INDEX_URL,
        headers=HEADERS,
        timeout=30,
    )

    response.raise_for_status()

    return response.text


def extract_words(html):

    soup = BeautifulSoup(html, "html.parser")

    words = []
    seen = set()

    for link in soup.select("a[href^='/wiki/']"):

        word = link.get_text(strip=True)

        if not word:
            continue

        if ":" in word:
            continue

        if len(word) < 2:
            continue

        if not re.match(
            r"^[A-Za-zÀ-ÖØ-öø-ÿ' -]+$",
            word
        ):
            continue

        href = link.get("href", "")

        if "Indeks:" in href:
            continue

        if word in seen:
            continue

        seen.add(word)
        words.append(word)

    return words


def create_word_files(words):

    created = 0
    skipped = 0

    for rank, word in enumerate(
        words,
        start=1
    ):

        filename = (
            WORDS_DIR /
            f"{word}.json"
        )

        if filename.exists():
            skipped += 1
            continue

        payload = build_skeleton(
            word,
            rank
        )

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                payload,
                f,
                ensure_ascii=False,
                indent=2
            )

        created += 1

    return created, skipped


def main():

    print(
        "Downloading Wiktionary index..."
    )

    html = fetch_index()

    words = extract_words(html)

    print(
        f"Found {len(words)} words"
    )

    created, skipped = (
        create_word_files(words)
    )

    print(
        f"Created: {created}"
    )

    print(
        f"Skipped: {skipped}"
    )


if __name__ == "__main__":
    main()
