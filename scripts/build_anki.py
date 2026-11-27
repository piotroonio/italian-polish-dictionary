#!/usr/bin/env python3

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

WORDS_DIR = ROOT / "words"
EXPORT_DIR = ROOT / "exports"

EXPORT_DIR.mkdir(exist_ok=True)

output_file = EXPORT_DIR / "anki.csv"

with open(
    output_file,
    "w",
    encoding="utf-8",
    newline=""
) as csvfile:

    writer = csv.writer(csvfile)

    writer.writerow([
        "Italian",
        "Polish",
        "ExampleIT",
        "ExamplePL",
        "CEFR",
        "FrequencyRank"
    ])

    for json_file in sorted(
        WORDS_DIR.glob("*.json")
    ):

        with open(
            json_file,
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        italian = data["lemma"]

        cefr = data.get(
            "cefr",
            ""
        )

        frequency = data.get(
            "frequency_rank",
            ""
        )

        for sense in data.get(
            "senses",
            []
        ):

            translations = sense.get(
                "translations",
                []
            )

            translation = (
                "; ".join(translations)
                if translations
                else ""
            )

            example_it = ""
            example_pl = ""

            examples = sense.get(
                "examples",
                []
            )

            if examples:

                example_it = examples[0].get(
                    "it",
                    ""
                )

                example_pl = examples[0].get(
                    "pl",
                    ""
                )

            writer.writerow([
                italian,
                translation,
                example_it,
                example_pl,
                cefr,
                frequency
            ])

print(
    f"Generated {output_file}"
)
