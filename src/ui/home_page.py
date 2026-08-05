import sys

from pathlib import Path

from .module_card import ModuleCard

from core.settings_manager import settings_manager

from core.translation_manager import (
    tr,
    translation_manager,
)

from PySide6.QtCore import (
    Qt,
    QSize,
    Signal,
)

from PySide6.QtGui import (
    QPixmap,
    QIcon,
)

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QComboBox,
)


class HomePage(QWidget):

    language_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setup_ui()


    def setup_ui(self):

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            40,
            30,
            40,
            30
        )

        main_layout.setSpacing(20)

        # -------------------------
        # Sélecteur de langue
        # -------------------------

        language_layout = QHBoxLayout()
        language_layout.addStretch()

        self.language_combo = QComboBox()

        self.language_combo.setIconSize(
            QSize(24, 16)
        )

        # -------------------------
        # Drapeaux
        # -------------------------

        if getattr(sys, "frozen", False):

            flags_path = (
                Path(sys._MEIPASS)
                / "resources"
                / "images"
                / "flags"
            )

        else:

            flags_path = (
                Path(__file__).resolve().parent.parent.parent
                / "resources"
                / "images"
                / "flags"
            )

            test_icon = QIcon(
            str(flags_path / "fr.png")
        )
            
        self.language_combo.addItem(
            QIcon(
                str(flags_path / "fr.png")
            ),
            "Français"
        )

        self.language_combo.addItem(
            QIcon(
                str(flags_path / "gb.png")
            ),
            "English"
        )

        self.language_combo.addItem(
            QIcon(
                str(flags_path / "de.png")
            ),
            "Deutsch"
        )

        self.language_combo.addItem(
            QIcon(
                str(flags_path / "es.png")
            ),
            "Español"
        )

        self.language_combo.currentIndexChanged.connect(
            self.change_language
        )
    

        self.language_combo.setFixedWidth(150)

        self.language_combo.setStyleSheet("""
            QComboBox {
                background-color: #292d32;
                color: #ffffff;
                border: 1px solid #3c4248;
                border-radius: 7px;
                padding: 7px 10px;
                font-size: 13px;
            }

            QComboBox:hover {
                border: 1px solid #e3262e;
            }

            QComboBox::drop-down {
                border: none;
                width: 24px;
            }

            QComboBox QAbstractItemView {
                background-color: #292d32;
                color: #ffffff;
                selection-background-color: #e3262e;
                border: 1px solid #3c4248;
            }
        """)

        language_layout.addWidget(self.language_combo)

        main_layout.addLayout(language_layout)

        # -------------------------
        # Logo / en-tête
        # -------------------------

        self.logo_label = QLabel()

        # Chemin compatible développement + application compilée
        if getattr(sys, "frozen", False):

            logo_path = (
                Path(sys._MEIPASS)
                / "resources"
                / "images"
                / "companion_logo.png"
            )

        else:

            logo_path = (
                Path(__file__).resolve().parent.parent.parent
                / "resources"
                / "images"
                / "companion_logo.png"
            )

        logo_pixmap = QPixmap(
            str(logo_path)
        )

        self.logo_label.setPixmap(
            logo_pixmap.scaled(
                650,
                260,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

        self.logo_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        main_layout.addWidget(
            self.logo_label
        )

        self.subtitle_label = QLabel(
            tr(
                "home_subtitle",
                "Votre compagnon pour Supermarket Together"
            )
        )

        self.subtitle_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.subtitle_label.setStyleSheet("""
            color: #9ca3af;
            font-size: 14px;
        """)

        main_layout.addWidget(
            self.subtitle_label
        )

        # -------------------------
        # Modules principaux
        # -------------------------

        modules_layout = QHBoxLayout()

        modules_layout.setSpacing(
            25
        )

        self.card_companion_table = ModuleCard(
            "📋",
            "SMT Companion Table",
            "Consulter et gérer le catalogue complet des produits"
        )

        self.card_price_checker = ModuleCard(
            "💲",
            "Price Checker",
            "Optimiser rapidement le prix de vente possible "
            "par rapport au prix du marché"
        )

        # -------------------------
        # Restauration de la langue
        # -------------------------

        saved_language = settings_manager.get(
            "language",
            "fr"
        )

        language_indexes = {
            "fr": 0,
            "en": 1,
            "de": 2,
            "es": 3,
        }

        saved_index = language_indexes.get(
            saved_language,
            0
        )

        self.language_combo.setCurrentIndex(
            saved_index
        )

        self.change_language(
            saved_index
        )

        modules_layout.addWidget(
            self.card_companion_table
        )

        modules_layout.addWidget(
            self.card_price_checker
        )

        main_layout.addLayout(
            modules_layout
        )

        main_layout.addStretch()


    def change_language(
        self,
        index
    ):

        languages = [
            "fr",
            "en",
            "de",
            "es"
        ]

        language = languages[index]

        translation_manager.set_language(
            language
        )

        settings_manager.set(
            "language",
            language
        )

        self.language_changed.emit(
            language
        )

        # -------------------------
        # Mise à jour de la Home
        # -------------------------

        self.subtitle_label.setText(
            tr(
                "home_subtitle",
                "Votre compagnon pour Supermarket Together"
            )
        )

        self.card_companion_table.title_label.setText(
            "📋   " + tr(
                "companion_table_title",
                "SMT Companion Table"
            )
        )

        self.card_companion_table.description_label.setText(
            tr(
                "companion_table_description",
                "Consulter et gérer le catalogue complet des produits"
            )
        )

        self.card_price_checker.title_label.setText(
            "💲   " + tr(
                "price_checker_title",
                "Price Checker"
            )
        )

        self.card_price_checker.description_label.setText(
            tr(
                "price_checker_description",
                "Optimiser rapidement le prix de vente possible "
                "par rapport au prix du marché"
            )
        )