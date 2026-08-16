import json
import sys

from pathlib import Path

from core.game._localization._manager import game_localization_manager
from core import translation_manager
from core.translation_manager import tr
from core.translation_manager import translation_manager

from PySide6.QtGui import (
    QFontMetrics, 
    QIcon,
    QPixmap,
)
from PySide6.QtCore import (
    Qt,
    QSize,
)
from PySide6.QtWidgets import (
    QHeaderView,
    QTableWidgetItem,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QAbstractItemView,
    QScrollArea,
    QFrame
)


class CompanionTablePage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.subcategory_buttons = []

        self.setup_ui()


    def setup_ui(self):

        main_layout = QHBoxLayout(self)

        main_layout.setContentsMargins(
            40,
            30,
            40,
            30
        )

        main_layout.setSpacing(20)

        # -------------------------
        # Colonne des catégories
        # -------------------------

        self.categories_panel = QWidget()

        self.categories_panel.setFixedWidth(
            240
        )

        self.categories_panel.setObjectName(
            "categoriesPanel"
        )

        self.categories_panel.setStyleSheet("""
            QWidget#categoriesPanel {
                background-color: #23272b;
                border: 1px solid #3c4248;
                border-radius: 12px;
            }
        """)

        categories_layout = QVBoxLayout(
            self.categories_panel
        )

        categories_layout.setContentsMargins(
            12,
            16,
            12,
            16
        )

        categories_layout.setSpacing(
            6
        )

        self.categories_title = QLabel(
            tr(
                "categories_title",
                "Catégories"
            )
        )

        self.categories_title.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 16px;
                font-weight: 600;
                padding: 4px 8px 12px 8px;
                border: none;
            }
        """)

        categories_layout.addWidget(
            self.categories_title
        )

        # -------------------------
        # Zone scrollable catégories
        # -------------------------

        self.categories_scroll = QScrollArea()

        self.categories_scroll.setWidgetResizable(
            True
        )

        self.categories_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.categories_scroll.setFrameShape(
            QScrollArea.Shape.NoFrame
        )

        self.categories_scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }

            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                margin: 2px 0px;
            }

            QScrollBar::handle:vertical {
                background: #4b5158;
                border-radius: 4px;
                min-height: 30px;
            }

            QScrollBar::handle:vertical:hover {
                background: #626971;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)

        self.categories_container = QWidget()

        self.categories_container.setStyleSheet("""
            background: transparent;
            border: none;
        """)

        self.categories_buttons_layout = QVBoxLayout(
            self.categories_container
        )

        self.categories_buttons_layout.setContentsMargins(
            0,
            4,
            4,
            4
        )

        self.categories_buttons_layout.setSpacing(
            3
        )

        self.categories_scroll.setWidget(
            self.categories_container
        )

        categories_layout.addWidget(
            self.categories_scroll,
            1
        )

        # -------------------------
        # Boutons des catégories
        # -------------------------

        self.category_buttons = {}
        self.category_section_buttons = {}
        self.category_section_containers = {}

        # -------------------------
        # Chargement des catégories wiki
        # -------------------------

        if getattr(sys, "frozen", False):

            categories_path = (
                Path(sys._MEIPASS)
                / "data"
                / "categories.json"
            )

        else:

            categories_path = (
                Path(__file__).resolve().parent.parent
                / "data"
                / "categories.json"
            )

        with open(
            categories_path,
            "r",
            encoding="utf-8"
        ) as file:

            categories_data = json.load(
                file
            )

        self.categories = categories_data.get(
            "categories",
            []
        )

        for category in self.categories:

            category_key = category[
                "id"
            ]

            category_name = (
                game_localization_manager.get_application_category_name(
                    category_key
                )
                or category[
                    "name"
                ]
            )

            sections = category.get(
                "sections",
                []
            )

            # -------------------------
            # Groupe de catégorie
            # -------------------------

            group_widget = QFrame()

            group_layout = QVBoxLayout(
                group_widget
            )

            group_layout.setContentsMargins(
                0,
                0,
                0,
                0
            )

            group_layout.setSpacing(
                2
            )

            # -------------------------
            # Bouton catégorie principale
            # -------------------------

            button = QPushButton(
                "›  " + category_name
            )

            # -------------------------
            # Icône de la catégorie
            # -------------------------

            if getattr(
                sys,
                "frozen",
                False
            ):

                icon_path = (
                    Path(sys._MEIPASS)
                    / "resources"
                    / "images"
                    / "categories"
                    / f"{category_key}.png"
                )

            else:

                icon_path = (
                    Path(__file__).resolve()
                    .parent.parent.parent
                    / "resources"
                    / "images"
                    / "categories"
                    / f"{category_key}.png"
                )

            if icon_path.exists():

                button.setIcon(
                    QIcon(
                        str(icon_path)
                    )
                )

                button.setIconSize(
                    QSize(
                        26,
                        26
                    )
                )

            button.setCursor(
                Qt.CursorShape.PointingHandCursor
            )

            button.setMinimumHeight(
                40
            )

            button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #d1d5db;
                border: none;
                border-radius: 7px;
                padding: 5px 8px;
                text-align: left;
                font-size: 13px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #30353a;
                color: #ffffff;
            }

            QPushButton:pressed {
                background-color: #383e44;
            }
        """)

            group_layout.addWidget(
                button
            )

            self.category_buttons[
                category_key
            ] = button

            # -------------------------
            # Conteneur sous-catégories
            # -------------------------

            sections_widget = QWidget()

            sections_layout = QVBoxLayout(
                sections_widget
            )

            sections_layout.setContentsMargins(
                18,
                0,
                0,
                4
            )

            sections_layout.setSpacing(
                1
            )

            for section in sections:

                section_key = section[
                    "id"
                ]

                section_name = (
                    game_localization_manager.get_application_section_name(
                        section_key
                    )
                    or section[
                        "name"
                    ]
                )

                section_button = QPushButton(
                    section_name
                )

                self.subcategory_buttons.append(
                    section_button
                )

                section_button.setCursor(
                    Qt.CursorShape.PointingHandCursor
                )

                section_button.setMinimumHeight(
                    32
                )

                section_button.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #9ca3af;
                        border: none;
                        border-radius: 6px;
                        padding: 5px 8px;
                        text-align: left;
                        font-size: 12px;
                    }

                    QPushButton:hover {
                        background-color: #30353a;
                        color: #ffffff;
                    }

                    QPushButton[active="true"] {
                        background-color: #30353a;
                        color: #ffffff;
                        border-left: 3px solid #e3262e;
                        font-weight: 600;
                    }
                """)

                sections_layout.addWidget(
                    section_button
                )

                self.category_section_buttons[
                    section_key
                ] = section_button

                section_button.clicked.connect(
                    lambda checked=False,
                    key=section_key:
                    self.show_section_products(
                        key
                    )
                )

            # Fermé par défaut.
            sections_widget.setVisible(
                False
            )

            group_layout.addWidget(
                sections_widget
            )

            self.category_section_containers[
                category_key
            ] = sections_widget

            button.clicked.connect(
                lambda checked=False,
                key=category_key:
                self.toggle_category(
                    key
                )
            )

            self.categories_buttons_layout.addWidget(
                group_widget
            )

        self.categories_buttons_layout.addStretch()

        main_layout.addWidget(
            self.categories_panel
        )

        # -------------------------
        # Chargement des produits wiki
        # -------------------------

        if getattr(sys, "frozen", False):

            products_path = (
                Path(sys._MEIPASS)
                / "data"
                / "products.json"
            )

        else:

            products_path = (
                Path(__file__).resolve().parent.parent
                / "data"
                / "products.json"
            )

        with open(
            products_path,
            "r",
            encoding="utf-8"
        ) as file:

            products_data = json.load(
                file
            )

        self.products = products_data.get(
            "products",
            []
        )

        # -------------------------
        # Contenu principal
        # -------------------------

        self.content_widget = QWidget()

        content_layout = QVBoxLayout(
            self.content_widget
        )

        content_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        content_layout.setSpacing(
            16
        )

        main_layout.addWidget(
            self.content_widget,
            1
        )

        # -------------------------
        # Header
        # -------------------------

        header_layout = QHBoxLayout()

        self.btn_home = QPushButton(
            "⌂  " + tr(
                "button_home",
                "Accueil"
            )
        )

        self.btn_home.setFixedHeight(
            42
        )

        self.btn_home.setMinimumWidth(
            125
        )

        self.btn_home.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.btn_home.setStyleSheet("""
            QPushButton {
                background-color: #292d32;
                color: #ffffff;
                border: 1px solid #3c4248;
                border-radius: 8px;
                padding: 0px 16px;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #32373d;
                border: 1px solid #e3262e;
            }

            QPushButton:pressed {
                background-color: #202327;
            }
        """)

        self.title_label = QLabel(
            "SMT Companion Table"
        )

        self.title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: 600;
            color: #ffffff;
        """)

        header_layout.addWidget(
            self.btn_home
        )

        header_layout.addSpacing(
            15
        )

        header_layout.addWidget(
            self.title_label
        )

        header_layout.addStretch()

        content_layout.addLayout(
            header_layout
        )

        # -------------------------
        # Barre de recherche
        # -------------------------

        search_layout = QHBoxLayout()

        self.search_bar = QLineEdit()

        self.search_bar.setPlaceholderText(
            tr(
                "companion_table_search_placeholder",
                "Rechercher un produit..."
            )
        )

        self.search_bar.setClearButtonEnabled(
            True
        )

        self.search_bar.setMinimumHeight(
            44
        )

        self.search_bar.setStyleSheet("""
            QLineEdit {
                background-color: #292d32;
                color: #ffffff;
                border: 1px solid #3c4248;
                border-radius: 10px;
                padding: 0px 16px;
                font-size: 14px;
            }

            QLineEdit:hover {
                border: 1px solid #555c64;
            }

            QLineEdit:focus {
                border: 1px solid #e3262e;
                background-color: #2d3237;
            }
        """)

        search_layout.addWidget(
            self.search_bar
        )

        content_layout.addLayout(
            search_layout
        )

        # -------------------------
        # Message d'attente
        # -------------------------

        self.selection_message = QLabel(
            tr(
                "companion_table_select_subcategory",
                "Veuillez sélectionner une sous-catégorie de produit pour commencer"
            )
        )

        self.selection_message.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.selection_message.setStyleSheet("""
            QLabel {
                color: #9ca3af;
                font-size: 16px;
                font-weight: 500;
                padding: 40px;
            }
        """)

        content_layout.addWidget(
            self.selection_message,
            1
        )

        # -------------------------
        # Tableau prix / rentabilité
        # -------------------------

        self.price_table = QTableWidget()

        # Colonnes : Image, Produit, Marque, Prix / carton, Prix unitaire
        self.price_table.setColumnCount(
            5
        )

        self.price_table.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.price_table.setHorizontalHeaderLabels([
            tr(
                "table_image",
                "Image"
            ),
            tr(
                "table_product",
                "Produit"
            ),
            tr(
                "table_brand",
                "Marque"
            ),
            tr(
                "table_price_per_box",
                "Prix / carton"
            ),
            tr(
                "table_price_per_unit",
                "Prix unitaire"
            ),
        ])

        self.price_table.horizontalHeader().setMinimumHeight(
            60
        )

        self.price_table.horizontalHeader().setDefaultAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.price_table.setAlternatingRowColors(
            True
        )

        self.price_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.price_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.price_table.setShowGrid(
            False
        )

        self.price_table.verticalHeader().setVisible(
            False
        )

        self.price_table.verticalHeader().setDefaultSectionSize(
            60
        )

        self.price_table.setStyleSheet("""
            QTableWidget {
                background-color: #23272b;
                alternate-background-color: #292d32;
                color: #ffffff;
                border: 1px solid #3c4248;
                border-radius: 10px;
                font-size: 14px;
            }

            QTableWidget::item {
                padding: 10px;
                border: none;
            }

            QTableWidget::item:selected {
                background-color: #3a3f45;
            }

            QHeaderView::section {
                background-color: #292d32;
                color: #ffffff;
                border: none;
                border-bottom: 1px solid #3c4248;
                padding: 10px;
                font-weight: 600;
            }
        """)

        # -------------------------
        # Tableau stockage
        # -------------------------

        self.storage_table = QTableWidget()

        self.storage_table.setColumnCount(
            7
        )

        self.storage_table.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.storage_table.setHorizontalHeaderLabels([
            tr(
                "table_image",
                "Image"
            ),
            tr(
                "table_product",
                "Produit"
            ),
            tr(
                "table_amount_per_box",
                "Qté / carton"
            ),
            tr(
                "table_small_shelf_quantity",
                "Qté / petite étagère"
            ),
            tr(
                "table_small_shelf_ratio",
                "Ratio carton / petite étagère"
            ),
            tr(
                "table_large_shelf_quantity",
                "Qté / grande étagère"
            ),
            tr(
                "table_large_shelf_ratio",
                "Ratio carton / grande étagère"
            ),
        ])

        self.storage_table.horizontalHeader().setMinimumHeight(
            60
        )

        self.storage_table.horizontalHeader().setDefaultAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.storage_table.setAlternatingRowColors(
            True
        )

        self.storage_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.storage_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.storage_table.setShowGrid(
            False
        )

        self.storage_table.verticalHeader().setVisible(
            False
        )

        self.storage_table.verticalHeader().setDefaultSectionSize(
            60
        )

        self.storage_table.setStyleSheet("""
            QTableWidget {
                background-color: #23272b;
                alternate-background-color: #292d32;
                color: #ffffff;
                border: 1px solid #3c4248;
                border-radius: 10px;
                font-size: 14px;
            }

            QTableWidget::item {
                padding: 10px;
                border: none;
            }

            QTableWidget::item:selected {
                background-color: #3a3f45;
            }

            QHeaderView::section {
                background-color: #292d32;
                color: #ffffff;
                border: none;
                border-bottom: 1px solid #3c4248;
                padding: 12px;
                font-weight: 600;
            }
        """)

        # -------------------------
        # Ajout des deux tableaux
        # -------------------------

        content_layout.addWidget(
            self.price_table
        )

        content_layout.addWidget(
            self.storage_table
        )

        self.price_table.hide()

        self.storage_table.hide()


    def toggle_category(
        self,
        category_key
    ):

        sections_widget = (
            self.category_section_containers[
                category_key
            ]
        )

        is_open = (
            sections_widget.isVisible()
        )

        sections_widget.setVisible(
            not is_open
        )

        category = next(
            (
                item
                for item in self.categories
                if item["id"] == category_key
            ),
            None
        )

        if category is None:
            return

        category_name = (
            game_localization_manager.get_application_category_name(
                category_key
            )
            or category[
                "name"
            ]
        )

        arrow = (
            "⌄"
            if not is_open
            else "›"
        )

        self.category_buttons[
            category_key
        ].setText(
            f"{arrow}  {category_name}"
        )


    def parse_price(
        self,
        value
    ):

        if value is None:
            return None

        text = str(
            value
        ).strip()

        if not text:
            return None

        text = (
            text
            .replace("$", "")
            .replace(",", ".")
            .strip()
        )

        try:

            return float(
                text
            )

        except ValueError:

            return None


    def show_section_products(
        self,
        section_key
    ):

        self.selection_message.hide()

        self.price_table.show()

        self.storage_table.show()

        section = next(
            (
                item
                for category in self.categories
                for item in category.get(
                    "sections",
                    []
                )
                if item["id"] == section_key
            ),
            None
        )

        if section is not None:

            section_name = (
                game_localization_manager.get_application_section_name(
                    section_key
                )
                or section[
                    "name"
                ]
            )

            self.title_label.setText(
                section_name
            )

            selected_button = (
                self.category_section_buttons.get(
                    section_key
                )
            )

            for button in self.subcategory_buttons:

                button.setProperty(
                    "active",
                    button is selected_button
                )

                button.style().unpolish(
                    button
                )

                button.style().polish(
                    button
                )

        section_products = [
            product
            for product in self.products
            if product.get("section_id")
            == section_key
        ]

        self.price_table.setRowCount(
            len(section_products)
        )

        self.storage_table.setRowCount(
            len(section_products)
        )

        for row, product in enumerate(
            section_products
        ):

            price_per_box = product.get(
                "price_per_box",
                ""
            )

            price_per_unit = product.get(
                "price_per_unit",
                ""
            )

            unit_price = self.parse_price(
                price_per_unit
            )

            market_price = None

            if unit_price is not None:

                market_price = (
                    unit_price * 1.95
                )

            margin = None

            if market_price is not None:

                margin = (
                    market_price
                    - unit_price
                )

            market_price_text = (
                ""
                if market_price is None
                else f"${market_price:.2f}"
            )

            margin_text = (
                ""
                if margin is None
                else f"${margin:.2f}"
            )

            product_name = (
                game_localization_manager.get_application_product_name(
                    section_key,
                    row
            )
                or product.get(
                    "name",
                    ""
                )
            )

            brand = product.get(
                "brand",
                ""
            )

            amount_per_box = product.get(
                "amount_per_box",
                ""
            )

            # -------------------------
            # Tableau prix / rentabilité
            # -------------------------

            image_item = QTableWidgetItem()

            image_path = product.get(
                "image_path",
                ""
            )

            if image_path:

                pixmap = QPixmap(
                    image_path
                )

                if not pixmap.isNull():

                    image_item.setData(
                        Qt.ItemDataRole.DecorationRole,
                        pixmap.scaled(
                            50,
                            50,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation
                        )
                    )

            self.price_table.setItem(
                row,
                0,
                image_item
            )

            self.price_table.setItem(
                row,
                1,
                QTableWidgetItem(
                    product_name
                )
            )

            self.price_table.setItem(
                row,
                2,
                QTableWidgetItem(
                    brand
                )
            )

            self.price_table.setItem(
                row,
                3,
                QTableWidgetItem(
                    price_per_box
                )
            )

            self.price_table.setItem(
                row,
                4,
                QTableWidgetItem(
                    price_per_unit
                )
            )

            # -------------------------
            # Tableau stockage
            # -------------------------

            storage_image_item = (
                QTableWidgetItem()
            )

            image_path = product.get(
                "image_path",
                ""
            )

            if image_path:

                pixmap = QPixmap(
                    image_path
                )

                if not pixmap.isNull():

                    storage_image_item.setData(
                        Qt.ItemDataRole.DecorationRole,
                        pixmap.scaled(
                            50,
                            50,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation
                        )
                    )

            self.storage_table.setItem(
                row,
                0,
                storage_image_item
            )

            self.storage_table.setItem(
                row,
                1,
                QTableWidgetItem(
                    product_name
                )
            )

            self.storage_table.setItem(
                row,
                2,
                QTableWidgetItem(
                    amount_per_box
                )
            )

            for column in range(
                3,
                7
            ):

                self.storage_table.setItem(
                    row,
                    column,
                    QTableWidgetItem(
                        ""
                    )
                )

        self.price_table.resizeColumnsToContents()

        self.storage_table.resizeColumnsToContents()


    def retranslate_ui(self):



        self.btn_home.setText(
            "⌂  " + tr(
                "button_home",
                "Accueil"
            )
        )

        self.title_label.setText(
            tr(
                "companion_table_title",
                "SMT Companion Table"
            )
        )

        self.search_bar.setPlaceholderText(
            tr(
                "companion_table_search_placeholder",
                "Rechercher un produit..."
            )
        )

        self.categories_title.setText(
            tr(
                "categories_title",
                "Catégories"
            )
        )

        # -------------------------
        # Localisation des catégories du jeu
        # -------------------------

        game_localization_manager.set_language(
            translation_manager.current_language
        )

        for category in self.categories:

            category_key = category[
                "id"
            ]

            category_name = (
                game_localization_manager.get_application_category_name(
                    category_key
                )
                or category[
                    "name"
                ]
            )

            self.category_buttons[
                category_key
            ].setText(
                category_name
            )

        # -------------------------
        # Localisation des sous-catégories du jeu
        # -------------------------

        for category in self.categories:

            for section in category.get(
                "sections",
                []
            ):

                section_key = section[
                    "id"
                ]

                section_name = (
                    game_localization_manager.get_application_section_name(
                        section_key
                    )
                    or section[
                        "name"
                    ]
                )

                button = (
                    self.category_section_buttons.get(
                        section_key
                    )
                )

                if button is not None:

                    button.setText(
                        section_name
                    )

        # -------------------------
        # Traduction du tableau prix
        # -------------------------

        self.price_table.setHorizontalHeaderLabels([
            tr(
                "table_image",
                "Image"
            ),
            tr(
                "table_product",
                "Produit"
            ),
            tr(
                "table_brand",
                "Marque"
            ),
            tr(
                "table_price_per_box",
                "Prix / carton"
            ),
            tr(
                "table_price_per_unit",
                "Prix unitaire"
            ),
        ])

        self.price_table.horizontalHeader().setMinimumHeight(
            60
        )

        self.price_table.horizontalHeader().setDefaultAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        # -------------------------
        # Traduction du tableau stockage
        # -------------------------

        self.storage_table.setHorizontalHeaderLabels([
            tr(
                "table_image",
                "Image"
            ),
            tr(
                "table_product",
                "Produit"
            ),
            tr(
                "table_amount_per_box",
                "Qté / carton"
            ),
            tr(
                "table_small_shelf_quantity",
                "Qté / petite étagère"
            ),
            tr(
                "table_small_shelf_ratio",
                "Ratio carton / petite étagère"
            ),
            tr(
                "table_large_shelf_quantity",
                "Qté / grande étagère"
            ),
            tr(
                "table_large_shelf_ratio",
                "Ratio carton / grande étagère"
            ),
        ])

        self.storage_table.horizontalHeader().setMinimumHeight(
            60
        )

        self.storage_table.horizontalHeader().setDefaultAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.price_table.setWordWrap(
            False
        )

        self.storage_table.setWordWrap(
            False
        )

        self.price_table.resizeColumnsToContents()

        self.storage_table.resizeColumnsToContents()


    def resize_table_columns_to_content(
        self
    ):

        for table in (
            self.price_table,
            self.storage_table
        ):

            header = (
                table.horizontalHeader()
            )

            header_font = header.font()

            header_metrics = QFontMetrics(
                header_font
            )

            for column in range(
                table.columnCount()
            ):

                max_width = 0

                # -------------------------
                # Texte de l'en-tête
                # -------------------------

                header_item = (
                    table.horizontalHeaderItem(
                        column
                    )
                )

                if header_item is not None:

                    header_text = (
                        header_item.text()
                    )

                    for line in (
                        header_text.splitlines()
                    ):

                        max_width = max(
                            max_width,
                            header_metrics.horizontalAdvance(
                                line
                            )
                        )

                # -------------------------
                # Texte des cellules
                # -------------------------

                for row in range(
                    table.rowCount()
                ):

                    item = table.item(
                        row,
                        column
                    )

                    if item is None:
                        continue

                    item_text = (
                        item.text()
                    )

                    if not item_text:
                        continue

                    item_metrics = QFontMetrics(
                        item.font()
                    )

                    for line in (
                        item_text.splitlines()
                    ):

                        max_width = max(
                            max_width,
                            item_metrics.horizontalAdvance(
                                line
                            )
                        )

                # -------------------------
                # Marge totale
                # -------------------------

                width = (
                    max_width
                    + 30
                )

                # -------------------------
                # Largeur minimale image
                # -------------------------

                if column == 0:

                    width = max(
                        width,
                        70,
                        max_width + 30
                    )

                table.setColumnWidth(
                    column,
                    width
                )