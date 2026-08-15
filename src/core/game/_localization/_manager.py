import json

from pathlib import Path

from core.settings_manager import settings_manager


class GameLocalizationManager:

    def __init__(self):

        self.data_directory = (
            Path(__file__).resolve().parent.parent.parent.parent
            / "data"
            / "game"
            / "localization"
        )

        self.current_language = None
        self.data = {}

        self.load_language(
            settings_manager.get(
                "language",
                "fr"
            )
        )

    def load_language(
        self,
        language
    ):

        language = language.upper()

        file_path = (
            self.data_directory
            / f"{language}.json"
        )

        if not file_path.exists():

            raise FileNotFoundError(
                f"Fichier de localisation du jeu "
                f"introuvable : {file_path}"
            )

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as file:

                self.data = json.load(
                    file
                )

        except (
            json.JSONDecodeError,
            OSError
        ) as error:

            raise RuntimeError(
                f"Impossible de charger la "
                f"localisation du jeu : {file_path}"
            ) from error

        self.current_language = language

    def set_language(
        self,
        language
    ):

        language = language.upper()

        if language == self.current_language:

            return

        self.load_language(
            language
        )

    def reload_current_language(self):

        if self.current_language is None:

            return

        self.load_language(
            self.current_language
        )

    # -------------------------
    # Noms des produits
    # -------------------------

    def get_product_name(
        self,
        product_id
    ):

        return self.data.get(
            "products",
            {}
        ).get(
            product_id
        )

    # -------------------------
    # Noms des catégories du jeu
    # -------------------------

    def get_group_name(
        self,
        group_id
    ):

        return self.data.get(
            "product_groups",
            {}
        ).get(
            group_id
        )

    # -------------------------
    # Noms des sous-catégories du jeu
    # -------------------------

    def get_category_name(
        self,
        category_id
    ):

        return self.data.get(
            "product_categories",
            {}
        ).get(
            category_id
        )

    # -------------------------
    # Correspondance application
    # → catégories du jeu
    # -------------------------

    CATEGORY_GROUP_IDS = {

        "basic_products": "productGroup0",
        "dairy_products": "productGroup1",
        "soda_drinks": "productGroup2",
        "frozen_foods": "productGroup3",
        "hygiene": "productGroup4",
        "cleaning_products": "productGroup5",
        "sweets_and_snacks": "productGroup6",
        "meat": "productGroup7",
        "preserves": "productGroup8",
        "infusions": "productGroup9",
        "seafood": "productGroup10",
        "books_packs": "productGroup11",
        "alcoholic_drinks": "productGroup12",
        "pharmacy": "productGroup13",
        "produce": "productGroup14",
        "child_care": "productGroup15",
        "gardening": "productGroup16",
        "small_electronics": "productGroup17",
        "halloween": "productGroup18",
        "christmas": "productGroup18"
    }

    def get_application_category_name(
        self,
        category_id
    ):

        game_group_id = (
            self.CATEGORY_GROUP_IDS.get(
                category_id
            )
        )

        if game_group_id is None:

            return None

        return self.get_group_name(
            game_group_id
        )

    APPLICATION_SECTION_IDS = {

        "basic_products_i": "productCategory0",
        "basic_products_ii": "productCategory1",
        "basic_products_iii": "productCategory2",
        "basic_products_iv": "productCategory3",
        "basic_products_v": "productCategory4",
        "basic_products_vi": "productCategory5",
        "dairy_products_i": "productCategory6",
        "dairy_products_ii": "productCategory7",
        "soda_drinks_i": "productCategory8",
        "frozen_foods_i": "productCategory9",
        "frozen_foods_ii": "productCategory10",
        "hygiene_i": "productCategory11",
        "hygiene_ii": "productCategory12",
        "hygiene_iii": "productCategory13",
        "cleaning_products_i": "productCategory14",
        "cleaning_products_ii": "productCategory15",
        "sweets_and_snacks_i": "productCategory16",
        "sweets_and_snacks_ii": "productCategory17",
        "sweets_and_snacks_iii": "productCategory18",
        "sweets_and_snacks_iv": "productCategory19",
        "meat_i": "productCategory20",
        "preserves_i": "productCategory21",
        "infusions_i": "productCategory22",
        "seafood_i": "productCategory23",
        "books_packs_i": "productCategory24",
        "books_packs_ii": "productCategory25",
        "alcoholic_drinks_i": "productCategory26",
        "alcoholic_drinks_ii": "productCategory27",
        "alcoholic_drinks_iii": "productCategory28",
        "pharmacy_i": "productCategory29",
        "pharmacy_ii": "productCategory30",
        "produce_i": "productCategory31",
        "produce_ii": "productCategory32",
        "produce_iii": "productCategory33",
        "produce_iv": "productCategory34",
        "child_care_i": "productCategory35",
        "child_care_ii": "productCategory36",
        "soda_drinks_ii": "productCategory37",
        "soda_drinks_iii": "productCategory38",
        "sweets_and_snacks_v": "productCategory39",
        "sweets_and_snacks_vi": "productCategory40",
        "preserves_ii": "productCategory41",
        "gardening_i": "productCategory42",
        "gardening_ii": "productCategory43",
        "gardening_iii": "productCategory44",
        "gardening_iv": "productCategory45",
        "small_electronics_i": "productCategory46",
        "small_electronics_ii": "productCategory47",
        "small_electronics_iii": "productCategory48",
        "produce_v": "productCategory49",
        "sweets_and_snacks_vii": "productCategory50",
        "basic_products_vii": "productCategory51",
        "halloween": "productCategory52",
        "christmas": "productCategory53"
    }

    # -------------------------
    # Plages des produits du jeu
    # par sous-catégorie
    # -------------------------

    APPLICATION_PRODUCT_RANGES = {

        "basic_products_i": (
            0,
            5
        ),

        "basic_products_ii": (
            6,
            12
        ),

        "basic_products_iii": (
            13,
            19
        ),

        "basic_products_iv": (
            20,
            25
        ),

        "basic_products_v": (
            26,
            34
        ),

        "basic_products_vi": (
            35,
            42
        ),

        "dairy_products_i": (
            43,
            48
        ),

        "dairy_products_ii": (
            49,
            53  
        ),

        "soda_drinks_i": (
            54,
            60
        ),

        "frozen_foods_i": (
            61,
            67
        ),

        "frozen_foods_ii": (
            68,
            73
        ),

        "hygiene_i": (
            74,
            79
        ),

        "hygiene_ii": (
            80,
            84
        ),

        "hygiene_iii": (
            85,
            89
        ),

        "cleaning_products_i": (
            90,
            96
        ),

        "cleaning_products_ii": (
            97,
            103
        ),

        "sweets_and_snacks_i": (
            104,
            109
        ),

        "sweets_and_snacks_ii": (
            110,
            115
        ),

        "sweets_and_snacks_iii": (
            116,
            121
        ),

        "sweets_and_snacks_iv": (
            122,
            126
        ),

        "meat_i": (
            127,
            133
        ),

        "preserves_i": (
            134,
            139
        ),

        "infusions_i": (
            140,
            145
        ),

        "seafood_i": (
            146,
            149 
        ),

        "books_packs_i": (
            150,
            155
        ),

        "books_packs_ii": (
            156,
            161
        ),

        "alcoholic_drinks_i": (
            162,
            166
        ),

        "alcoholic_drinks_ii": (
            167,
            171
        ),

        "alcoholic_drinks_iii": (
            172,
            175
        ),

        "pharmacy_i": (
            176,
            182
        ),

        "pharmacy_ii": (
            183,
            190
        ),

        "produce_i": (
            191,
            196
        ),

        "produce_ii": (
            197,
            202
        ),

        "produce_iii": (
            203,
            208
        ),

        "produce_iv": (
            209,
            213
        ),

        "child_care_i": (
            214,
            219
        ),

        "child_care_ii": (
            220,
            226
        ),

        "soda_drinks_ii": (
            227,
            233
        ),

        "soda_drinks_iii": (
            234,
            240
        ),

        "sweets_and_snacks_v": (
            241,
            246
        ),

        "sweets_and_snacks_vi": (
            247,
            251
        ),

        "preserves_ii": (
            252,
            257
        ),

        "gardening_i": (
            258,
            262
        ),

        "gardening_ii": (
            263,
            267
        ),

        "gardening_iii": (
            268,
            272
        ),

        "gardening_iv": (
            273,
            280
        ),

        "small_electronics_i": (
            281,
            286
        ),

        "small_electronics_ii": (
            287,
            292
        ),

        "small_electronics_iii": (
            293,
            299
        ),

        "produce_v": (
            300,
            305
        ),

        "sweets_and_snacks_vii": (
            306,
            313
        ),

        "basic_products_vii": (
            314,
            321
        ),

        "halloween": (
            322,
            326
        ),

        "christmas": (
            327,
                330
        )
    }

    def get_application_section_name(
        self,
        section_id
    ):

        game_category_id = (
            self.APPLICATION_SECTION_IDS.get(
                section_id
            )
        )

        if game_category_id is None:

            return None

        return self.get_category_name(
            game_category_id
        )

    def get_application_product_name(
        self,
        section_id,
        position
    ):

        product_range = (
            self.APPLICATION_PRODUCT_RANGES.get(
                section_id
            )
        )

        if product_range is None:

            return None

        start_index, end_index = (
            product_range
        )

        product_index = (
            start_index
            + position
        )

        if product_index > end_index:

            return None

        return self.get_product_name(
            f"product{product_index}"
        )

    # -------------------------
    # Accès aux données complètes
    # -------------------------

    def get_products(self):

        return self.data.get(
            "products",
            {}
        )

    def get_categories(self):

        return self.data.get(
            "product_categories",
            {}
        )

    def get_groups(self):

        return self.data.get(
            "product_groups",
            {}
        )


game_localization_manager = (
    GameLocalizationManager()
)