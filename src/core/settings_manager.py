import json
import os

from pathlib import Path


class SettingsManager:

    DEFAULT_SETTINGS = {
        "language": "fr"
    }

    def __init__(self):

        # -------------------------
        # Dossier persistant Windows
        # -------------------------

        local_app_data = os.getenv(
            "LOCALAPPDATA"
        )

        if local_app_data:

            self.directory = (
                Path(local_app_data)
                / "SupermarketTogetherCompanion"
            )

        else:

            # Fallback, notamment pratique
            # pendant certains environnements de dev.
            self.directory = (
                Path.home()
                / ".SupermarketTogetherCompanion"
            )

        self.path = (
            self.directory
            / "settings.json"
        )

        self.settings = (
            self.DEFAULT_SETTINGS.copy()
        )

        self.load()


    def load(self):

        if not self.path.exists():

            self.save()
            return

        try:

            with open(
                self.path,
                "r",
                encoding="utf-8"
            ) as file:

                loaded_settings = json.load(
                    file
                )

            if isinstance(
                loaded_settings,
                dict
            ):

                self.settings.update(
                    loaded_settings
                )

        except (
            json.JSONDecodeError,
            OSError
        ):

            # Si le fichier est corrompu,
            # on repart sur les valeurs par défaut.
            self.settings = (
                self.DEFAULT_SETTINGS.copy()
            )

            self.save()


    def save(self):

        self.directory.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            self.path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.settings,
                file,
                ensure_ascii=False,
                indent=4
            )


    def get(
        self,
        key,
        default=None
    ):

        return self.settings.get(
            key,
            default
        )


    def set(
        self,
        key,
        value
    ):

        self.settings[key] = value

        # Sauvegarde immédiate.
        self.save()


settings_manager = SettingsManager()