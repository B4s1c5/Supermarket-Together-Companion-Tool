import json
import os
import sys

from pathlib import Path

import deepl

from dotenv import load_dotenv
from tree_sitter_javascript import language

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

        self.translation_total = 0
        self.translation_done = 0
        self.translation_failed = 0

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


    def prepare_translation_progress(
        self
    ):

        languages = (
            "fr",
            "en",
            "de",
            "es",
            "cz",
            "ch1",
            "ch2",
            "hu",
            "it",
            "jp",
            "kr",
            "pl",
            "pt",
            "ru",
            "uk",
        )

        total = 0
        done = 0

        for values in self.translations.values():

            if not isinstance(
                values,
                dict
            ):
                continue

            for language in languages:

                total += 1

                if values.get(
                    language
                ):
                    done += 1

        self.translation_total = total
        self.translation_done = done
        self.translation_failed = 0


    def display_translation_progress(
        self,
        key=None,
        language=None
    ):

        if getattr(
            sys,
            "frozen",
            False
        ):
            return

        if self.translation_total <= 0:
            return

        percent = int(
            self.translation_done
            / self.translation_total
            * 100
        )

        width = 30

        filled = int(
            width
            * percent
            / 100
        )

        bar = (
            "#" * filled
            + "-" * (
                width - filled
            )
        )

        message = ""

        if key and language:

            message = (
                f"{key} -> "
                f"{language.upper()}"
            )

        print(
            "\r"
            + " " * 120
            + "\r",
            end="",
            flush=True
        )

        print(
            f"[I18N]   [{bar}] "
            f"{percent:3d}%  "
            f"{self.translation_done} / "
            f"{self.translation_total}  "
            f"{message}",
            end="",
            flush=True
        )

    
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

        # Initialise le suivi avant
        # les traductions DeepL.
        if self.translation_total == 0:

            self.prepare_translation_progress()

        deepl_languages = {
            "fr": "FR",
            "en": "EN-US",
            "de": "DE",
            "es": "ES",
            "cz": "CS",
            "ch1": "ZH",
            "ch2": "ZH",
            "hu": "HU",
            "it": "IT",
            "jp": "JA",
            "kr": "KO",
            "pl": "PL",
            "pt": "PT-PT",
            "ru": "RU",
            "uk": "UK",
        }

        source_deepl_languages = {
            "fr": "FR",
            "en": "EN",
            "de": "DE",
            "es": "ES",
            "cz": "CS",
            "ch1": "ZH",
            "ch2": "ZH",
            "hu": "HU",
            "it": "IT",
            "jp": "JA",
            "kr": "KO",
            "pl": "PL",
            "pt": "PT",
            "ru": "RU",
            "uk": "UK",
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

                self.translation_done += 1

                self.display_translation_progress(
                    key,
                    language
                )

                modified = True

            except Exception as error:

                self.translation_failed += 1

                print(
                    "\r"
                    + " " * 120
                    + "\r",
                    end="",
                    flush=True
                )

                print(
                    f"[WARN] DeepL : "
                    f"{key} -> "
                    f"{language.upper()} "
                    f"non traduit"
                )

        if modified:
            self.save()


    def set_language(
        self,
        language
    ):

        language = language.lower()

        supported_languages = {
            "fr",
            "en",
            "de",
            "es",
            "cz",
            "ch1",
            "ch2",
            "hu",
            "it",
            "jp",
            "kr",
            "pl",
            "pt",
            "ru",
            "uk",
        }

        if language not in supported_languages:

            language = "fr"

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