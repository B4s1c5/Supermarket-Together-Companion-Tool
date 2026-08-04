import json
import os
import sys
import shutil
import deepl


from pathlib import Path
from dotenv import load_dotenv


class Translator:

    def __init__(self):

        if getattr(sys, "frozen", False):
            # Fichier de traductions fourni avec l'application
            bundled_path = (
                Path(sys._MEIPASS)
                / "data"
                / "translations.json"
            )

            # Cache utilisateur persistant
            appdata = os.getenv("LOCALAPPDATA")

            if not appdata:
                raise RuntimeError(
                    "Impossible de trouver le dossier LOCALAPPDATA."
                )

            user_data_dir = (
                Path(appdata)
                / "SupermarketTogetherCompanion"
            )

            user_data_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            self.path = (
                user_data_dir
                / "translations.json"
            )

            # Premier lancement : création du cache utilisateur
            if not self.path.exists():
                shutil.copy2(
                    bundled_path,
                    self.path
                )

        else:
            # En développement, on continue d'utiliser
            # directement le fichier du projet.
            self.path = (
                Path(__file__).resolve().parent.parent
                / "data"
                / "translations.json"
            )

        # Chargement du fichier .env
        # DeepL est disponible uniquement en développement.
        # La version distribuée utilise uniquement le cache local.
        self.deepl_translator = None

        if not getattr(sys, "frozen", False):
            load_dotenv()

            api_key = os.getenv("DEEPL_API_KEY")

            if api_key:
                self.deepl_translator = deepl.Translator(api_key)

        # Chargement du cache local
        with open(self.path, "r", encoding="utf-8") as file:

            self.translations = json.load(file)


    def translate(self, products):

        translated_count = 0
        unknown_count = 0
        unknown_products = []
        translation_results = []
        new_translation_results = []
        translation_errors = []

        # Produits nécessitant réellement DeepL
        missing_products = []

        # -------------------------
        # Recherche dans le cache
        # -------------------------

        for product in products:

            product_name = product.product_name

            if (
                product_name in self.translations
                and self.translations[product_name]
            ):

                translated_name = self.translations[product_name]

                product.translate(translated_name)

            else:

                missing_products.append(product)

        # -------------------------
        # Traduction DeepL par lots
        # -------------------------

        # Dans la version distribuée, DeepL est désactivé.
        # Les produits absents du cache resteront simplement inconnus.
        if self.deepl_translator is None:
            missing_products = []

        batch_size = 40

        for start in range(
            0,
            len(missing_products),
            batch_size
        ):

            batch = missing_products[
                start:start + batch_size
            ]

            texts = [
                product.product_name
                for product in batch
            ]

            try:

                results = self.deepl_translator.translate_text(
                    texts,
                    source_lang="EN",
                    target_lang="FR"
                )

                for product, result in zip(batch, results):

                    translated_name = result.text

                    product.translate(translated_name)

                    self.translations[
                        product.product_name
                    ] = translated_name

                    new_translation_results.append(
                        (
                            True,
                            f"{product.product_name} - {product.brand}"

                        )
                    )

                # Sauvegarde après chaque lot réussi
                self.save_translations()

            except Exception as error:

                error_message = str(error)

                if error_message not in translation_errors:

                    translation_errors.append(error_message)

        # -------------------------
        # Résultats
        # -------------------------

        for product in products:

            product_label = (
                f"{product.product_name} - {product.brand}"
            )

            if product.translated_name:

                translated_count += 1

                translation_results.append(
                    (True, product_label)
                )

            else:

                unknown_count += 1

                unknown_products.append(
                    product_label
                )

                translation_results.append(
                    (False, product_label)
                )

        return (
            products,
            translated_count,
            unknown_count,
            unknown_products,
            translation_results,
            translation_errors,
            new_translation_results
        )


    def save_translations(self):

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