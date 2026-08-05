import json
import os
import sys

from pathlib import Path

import deepl

from dotenv import load_dotenv

load_dotenv()


class TranslationManager:

    def __init__(self):

        self.current_language = "fr"

        # -------------------------
        # Chemin du fichier
        # -------------------------

        if getattr(sys, "frozen", False):

            self.path = (
                Path(sys._MEIPASS)
                / "data"
                / "ui_translations.json"
            )

        else:

            self.path = (
                Path(__file__).resolve().parent.parent
                / "data"
                / "ui_translations.json"
            )

        # -------------------------
        # Chargement
        # -------------------------

        if self.path.exists():

            with open(
                self.path,
                "r",
                encoding="utf-8"
            ) as file:

                self.translations = json.load(
                    file
                )

        else:

            self.translations = {}

            self.save()

        self.deepl_translator = None

        if not getattr(
            sys,
            "frozen",
            False
        ):

            api_key = os.getenv(
                "DEEPL_API_KEY"
            )

            if api_key:

                self.deepl_translator = (
                    deepl.Translator(
                        api_key
                    )
                )

    def tr(
        self,
        key,
        source_text,
        source_language="fr"
    ):

        # -------------------------
        # Nouvelle clé
        # -------------------------

        if key not in self.translations:

            self.translations[key] = {
                source_language: source_text
            }

            if not getattr(
                sys,
                "frozen",
                False
            ):

                self.save()

        # -------------------------
        # Mise à jour du texte source
        # -------------------------

        elif (
            self.translations[key].get(
                source_language
            )
            != source_text
        ):

            self.translations[key][
                source_language
            ] = source_text

            if not getattr(
                sys,
                "frozen",
                False
            ):

                self.save()

        # -------------------------
        # Traductions automatiques
        # -------------------------

        if not getattr(
            sys,
            "frozen",
            False
        ):

            self.auto_translate_missing(
                key,
                source_language
            )

        # -------------------------
        # Traduction demandée
        # -------------------------

        translation = (
            self.translations[key].get(
                self.current_language
            )
        )

        # Fallback vers le texte source.
        if not translation:

            translation = source_text

        return translation

    
    def auto_translate_missing(
        self,
        key,
        source_language="fr"
    ):

        # DeepL ne doit fonctionner
        # qu'en environnement de développement.
        if getattr(sys, "frozen", False):
            return

        if self.deepl_translator is None:
            return

        values = self.translations.get(
            key
        )

        if not isinstance(values, dict):
            return

        source_text = values.get(
            source_language
        )

        if not source_text:
            return

        deepl_languages = {
            "fr": "FR",
            "en": "EN-US",
            "de": "DE",
            "es": "ES",
        }

        source_deepl_languages = {
            "fr": "FR",
            "en": "EN",
            "de": "DE",
            "es": "ES",
        }

        modified = False

        for language, deepl_language in deepl_languages.items():

            # Inutile de traduire la langue source
            # vers elle-même.
            if language == source_language:
                continue

            if values.get(language):
                continue

            try:

                result = self.deepl_translator.translate_text(
                    source_text,
                    source_lang=source_deepl_languages[
                        source_language
                    ],
                    target_lang=deepl_language
                )

                values[language] = result.text

                modified = True

                print(
                    f"[i18n] {key} -> {language}"
                )

            except Exception as error:

                # Une panne Internet / DeepL ne doit
                # jamais empêcher l'application de démarrer.
                print(
                    f"[i18n] DeepL indisponible "
                    f"pour {key}/{language}: {error}"
                )

        if modified:
            self.save()


    def set_language(
        self,
        language
    ):

        self.current_language = language


    def save(self):

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            self.path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.translations,
                file,
                ensure_ascii=False,
                indent=4
            )


translation_manager = TranslationManager()


def tr(
    key,
    source_text,
    source_language="fr"
):

    return translation_manager.tr(
        key,
        source_text,
        source_language=source_language
    )