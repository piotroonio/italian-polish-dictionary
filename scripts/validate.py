#!/usr/bin/env python3

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORDS_DIR = ROOT / "words"

VALID_CEFR = {
    "A1",
    "A2",
    "B1",
    "B2",
    "C1",
    "C2",
    "unknown",
}

VALID_POS = {
    "noun",
    "verb",
    "adjective",
    "adverb",
    "pronoun",
    "preposition",
    "conjunction",
    "interjection",
    "article",
}

errors = []
ids = set()


def error(file_path, message):
    errors.append(f"{file_path}: {message}")


def validate_word_file(file_path):
    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

    except Exception as e:
        error(file_path, f"invalid JSON: {e}")
        return

    required = [
        "id",
        "lemma",
        "language",
        "part_of_speech",
        "senses",
        "metadata",
    ]

    for field in required:
        if field not in data:
            error(file_path, f"missing field '{field}'")

    if "id" not in data:
        return

    word_id = data["id"]

    if word_id in ids:
        error(file_path, f"duplicate id '{word_id}'")
    else:
        ids.add(word_id)

    lemma = data.get("lemma")

    if lemma:
        expected = f"{lemma}.json"
        if file_path.name != expected:
            error(
                file_path,
                f"filename should be '{expected}'",
            )

    cefr = data.get("cefr")

    if cefr and cefr not in VALID_CEFR:
        error(
            file_path,
            f"invalid CEFR '{cefr}'",
        )

    pos = data.get("part_of_speech")

    if pos and pos not in VALID_POS:
        error(
            file_path,
            f"invalid part_of_speech '{pos}'",
        )

    senses = data.get("senses", [])

    if not isinstance(senses, list) or len(senses) == 0:
        error(file_path, "senses must be a non-empty array")
        return

    has_translation = False

    for sense in senses:

        translations = sense.get("translations", [])

        if translations:
            has_translation = True

        if "examples" in sense:
            examples = sense["examples"]

            if not isinstance(examples, list):
                error(
                    file_path,
                    "examples must be an array",
                )
                continue

            for example in examples:

                if "it" not in example:
                    error(
                        file_path,
                        "example missing italian text",
                    )

                if "pl" not in example:
                    error(
                        file_path,
                        "example missing polish text",
                    )

    metadata = data.get("metadata")

    if not isinstance(metadata, dict):
        error(
            file_path,
            "metadata must be an object",
        )
        return

    for field in ["source", "created", "updated"]:

        if field not in metadata:
            error(
                file_path,
                f"metadata field '{field}' missing",
            )


def main():

    if not WORDS_DIR.exists():
        print(f"Directory not found: {WORDS_DIR}")
        sys.exit(1)

    json_files = sorted(
        WORDS_DIR.glob("*.json")
    )

    if not json_files:
        print("No words found.")
        sys.exit(1)

    for file in json_files:
        validate_word_file(file)

    if errors:

        print("VALIDATION FAILED\n")

        for err in errors:
            print(f"- {err}")

        sys.exit(1)

    print(
        f"VALIDATION PASSED ({len(json_files)} files)"
    )


if __name__ == "__main__":
    main()
