import json
import os

from pathlib import Path

import deepl
from dotenv import load_dotenv


# -------------------------
# Chemins du projet
# -------------------------

PROJECT_ROOT = (
    Path(__file__).resolve().parent.parent
)

TRANSLATIONS_PATH = (
    PROJECT_ROOT
    / "src"
    / "data"
    / "ui_translations.json"
)

ENV_PATH = (
    PROJECT_ROOT
    / ".env"
)


# -------------------------
# Chargement DeepL
# -------------------------

load_dotenv(
    ENV_PATH
)

api_key = os.getenv(
    "DEEPL_API_KEY"
)

if not api_key:

    raise RuntimeError(
        "DEEPL_API_KEY introuvable dans le fichier .env"
    )

translator = deepl.Translator(
    api_key
)


# -------------------------
# Chargement du JSON
# -------------------------

with open(
    TRANSLATIONS_PATH,
    "r",
    encoding="utf-8"
) as file:

    translations = json.load(
        file
    )


# -------------------------
# Langues DeepL
# -------------------------

languages = {
    "en": "EN-US",
    "de": "DE",
    "es": "ES",
}


# -------------------------
# Recherche des traductions
# manquantes
# -------------------------

translation_count = 0

for key, values in translations.items():

    # Ancien format éventuel :
    # on l'ignore pour l'instant.
    if not isinstance(
        values,
        dict
    ):

        continue

    french_text = values.get(
        "fr"
    )

    if not french_text:

        continue

    for language, deepl_language in languages.items():

        if values.get(
            language
        ):

            continue

        print(
            f"Traduction : {key} -> {language}"
        )

        result = translator.translate_text(
            french_text,
            source_lang="FR",
            target_lang=deepl_language
        )

        values[language] = (
            result.text
        )

        translation_count += 1


# -------------------------
# Sauvegarde
# -------------------------

with open(
    TRANSLATIONS_PATH,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        translations,
        file,
        ensure_ascii=False,
        indent=4
    )


print()

if translation_count:

    print(
        f"{translation_count} traduction(s) ajoutée(s)."
    )

else:

    print(
        "Toutes les traductions sont déjà à jour."
    )