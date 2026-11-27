#!/usr/bin/env python3

import json
import re
from pathlib import Path

import requests

API_URL = "https://pl.wiktionary.org/w/api.php"

ROOT = Path(__file__).resolve().parent.parent
WORDS_DIR = ROOT / "words"

HEADERS = {
    "User-Agent": "italian-polish-dictionary/1.0"
}

PARTS_OF_SPEECH = {
    "rzeczownik": "noun",
    "czasownik": "verb",
    "przymiotnik": "adjective",
    "przysłówek": "adverb",
    "zaimek": "pronoun",
    "przyimek": "preposition",
    "spójnik": "conjunction",
    "wykrzyknik": "interjection",
    "rodzajnik": "article"
}


def get_wikitext(title):

    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "titles": title,
        "format": "json",
        "formatversion": "2"
    }

    response = requests.get(
        API_URL,
        params=params,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    pages = data["query"]["pages"]

    if not pages:
        return None

    revisions = pages[0].get("revisions")

    if not revisions:
        return None

    return revisions[0]["content"]


def parse_part_of_speech(text):

    for polish_name, normalized in PARTS_OF_SPEECH.items():

        if polish_name in text.lower():
            return normalized

    return ""


def parse_translations(text):

    translations = set()

    patterns = [
        r"→\s*([^,\n;]+)",
        r"\:\s*([^,\n;]+)"
    ]

    for pattern in patterns:

        for match in re.findall(
            pattern,
            text,
            flags=re.IGNORECASE
        ):

            candidate = (
                match.strip()
                .strip("[]{}()")
            )

            if (
                1 < len(candidate) < 80
                and not candidate.startswith("http")
            ):
                translations.add(candidate)

    return sorted(translations)


def extract_italian_section(text):

    match = re.search(
        r"==\s*włoski\s*==(.+?)(==|\Z)",
        text,
        flags=re.DOTALL | re.IGNORECASE
    )

    if match:
        return match.group(1)

    return text


def update_word_file(file_path):

    with open(
        file_path,
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    rank = data.get(
        "frequency_rank",
        999999
    )

    if rank > 50:
        return False

    lemma = data["lemma"]

    print(
        f"Processing {lemma}"
    )

    wikitext = get_wikitext(lemma)

    if not wikitext:
        print(
            f"  no page found"
        )
        return False

    italian = extract_italian_section(
        wikitext
    )

    pos = parse_part_of_speech(
        italian
    )

    if pos:
        data["part_of_speech"] = pos

    sense = data["senses"][0]

    if not sense["translations"]:

        translations = parse_translations(
            italian
        )

        if translations:

            sense["translations"] = (
                translations[:10]
            )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )

    return True


def main():

    files = sorted(
        WORDS_DIR.glob("*.json")
    )

    processed = 0

    for file_path in files:

        try:

            if update_word_file(
                file_path
            ):
                processed += 1

        except Exception as e:

            print(
                f"ERROR {file_path.name}: {e}"
            )

    print(
        f"\nUpdated files: {processed}"
    )


if __name__ == "__main__":
    main()
