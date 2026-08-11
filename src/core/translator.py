import json
import sys

from core.translation_manager import translation_manager

from pathlib import Path


class Translator:

    def __init__(self):

        if getattr(sys, "frozen", False):

            self.path = (
                Path(sys._MEIPASS)
                / "data"
                / "products.json"
            )

        else:

            self.path = (
                Path(__file__).resolve().parent.parent
                / "data"
                / "products.json"
            )

        with open(
            self.path,
            "r",
            encoding="utf-8"
        ) as file:

            products_data = json.load(
                file
            )

        self.products = {
            product.get("name"): product
            for product in products_data.get(
                "products",
                []
            )
            if product.get("name")
        }

        self.current_language = (
            translation_manager.current_language
        )


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
        # Recherche dans products.json
        # -------------------------

        for product in products:

            product_name = product.product_name

            product_data = self.products.get(
                product_name
            )

            if not product_data:

                missing_products.append(
                    product
                )

                continue

            translations = product_data.get(
                "translations",
                {}
            )

            translated_name = translations.get(
                self.current_language
            )

            if translated_name:

                product.translate(
                    translated_name
                )

            else:

                missing_products.append(
                    product
                )

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