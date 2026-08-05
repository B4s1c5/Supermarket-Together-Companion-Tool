import json
import sys

from pathlib import Path

from PySide6.QtCore import Qt

from core.translation_manager import tr

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QAbstractItemView,
    QScrollArea
)


class CompanionTablePage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

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

            category_name = category[
                "name"
            ]

            button = QPushButton(
                tr(
                    f"category_{category_key}",
                    category_name,
                    source_language="en"
                )
            )

            button.setCursor(
                Qt.CursorShape.PointingHandCursor
            )

            button.setMinimumHeight(
                36
            )

            button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #d1d5db;
                    border: none;
                    border-radius: 7px;
                    padding: 7px 10px;
                    text-align: left;
                    font-size: 13px;
                }

                QPushButton:hover {
                    background-color: #30353a;
                    color: #ffffff;
                }

                QPushButton:pressed {
                    background-color: #3a2528;
                    color: #ff5a61;
                }
            """)

            self.categories_buttons_layout.addWidget(
                button
            )

            self.category_buttons[
                category_key
            ] = button

        self.categories_buttons_layout.addStretch()

        main_layout.addWidget(
            self.categories_panel
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
        # Tableau produits
        # -------------------------

        self.product_table = QTableWidget()

        self.product_table.setColumnCount(
            5
        )

        self.product_table.setHorizontalHeaderLabels([
            tr(
                "table_product",
                "Produit"
            ),
            tr(
                "table_category",
                "Catégorie"
            ),
            tr(
                "table_market_price",
                "Prix du marché"
            ),
            tr(
                "table_selling_price",
                "Prix conseillé"
            ),
            tr(
                "table_actions",
                "Actions"
            ),
        ])

        self.product_table.setAlternatingRowColors(
            True
        )

        self.product_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.product_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.product_table.setShowGrid(
            False
        )

        self.product_table.verticalHeader().setVisible(
            False
        )

        self.product_table.setStyleSheet("""
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

        content_layout.addWidget(
            self.product_table,
            1
        )


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
        # Traduction des catégories wiki
        # -------------------------

        for category in self.categories:

            category_key = category[
                "id"
            ]

            category_name = category[
                "name"
            ]

            self.category_buttons[
                category_key
            ].setText(
                tr(
                    f"category_{category_key}",
                    category_name,
                    source_language="en"
                )
            )