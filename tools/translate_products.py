import json
import os

from pathlib import Path

import deepl

from dotenv import load_dotenv


load_dotenv()


PROJECT_ROOT = (
    Path(__file__).resolve().parent.parent
)

PRODUCTS_PATH = (
    PROJECT_ROOT
    / "src"
    / "data"
    / "products.json"
)


API_KEY = os.getenv(
    "DEEPL_API_KEY"
)

if not API_KEY:

    raise RuntimeError(
        "DEEPL_API_KEY introuvable."
    )


translator = deepl.Translator(
    API_KEY
)


with open(
    PRODUCTS_PATH,
    "r",
    encoding="utf-8"
) as file:

    products_data = json.load(
        file
    )


products = products_data.get(
    "products",
    []
)


targets = {
    "fr": "FR",
    "de": "DE",
    "es": "ES",
}


for product in products:

    product_name = product.get(
        "name",
        ""
    )

    if not product_name:
        continue

    translations = product.setdefault(
        "translations",
        {}
    )

    missing_languages = [
        language
        for language in targets
        if not translations.get(language)
    ]

    if not missing_languages:
        continue

    print(
        f"[DEEPL] {product_name} -> "
        f"{', '.join(missing_languages).upper()}"
    )

    for language in missing_languages:

        result = translator.translate_text(
            product_name,
            source_lang="EN",
            target_lang=targets[
                language
            ]
        )

        translations[language] = (
            result.text
        )


    with open(
        PRODUCTS_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            products_data,
            file,
            ensure_ascii=False,
            indent=4
        )


print(
    "\n[DEEPL] Traductions terminées."
)