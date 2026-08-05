import json
import sys

from pathlib import Path


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


    def tr(
        self,
        key,
        french_text
    ):

        # -------------------------
        # Nouvelle clé
        # -------------------------

        if key not in self.translations:

            self.translations[key] = {
                "fr": french_text
            }

            # En développement uniquement,
            # on enrichit automatiquement le JSON.
            if not getattr(sys, "frozen", False):

                self.save()

        # -------------------------
        # Mise à jour du français
        # -------------------------

        elif (
            self.translations[key].get("fr")
            != french_text
        ):

            self.translations[key]["fr"] = (
                french_text
            )

            if not getattr(sys, "frozen", False):

                self.save()

        # -------------------------
        # Traduction demandée
        # -------------------------

        translation = (
            self.translations[key].get(
                self.current_language
            )
        )

        # Si la langue n'est pas encore traduite,
        # fallback automatique vers le français.
        if not translation:

            translation = (
                self.translations[key]["fr"]
            )

        return translation


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
    french_text
):

    return translation_manager.tr(
        key,
        french_text
    )