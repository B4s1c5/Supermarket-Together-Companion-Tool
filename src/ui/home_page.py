import sys

from pathlib import Path

from .module_card import ModuleCard

from core.translation_manager import (
    tr,
    translation_manager,
)

from core.game._localization._manager import (
    game_localization_manager,
)

from PySide6.QtCore import (
    Qt,
    QSize,
    Signal,
)

from PySide6.QtGui import (
    QPixmap,
    QAction,
    QIcon,
)

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QPushButton,
    QMenu,
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

        self.language_button = QPushButton(
            "🌐 Français"
        )

        self.language_button.setFixedWidth(
            150
        )

        self.language_button.setStyleSheet("""
            QPushButton {
                background-color: #292d32;
                color: #ffffff;
                border: 1px solid #3c4248;
                border-radius: 7px;
                padding: 7px 10px;
                font-size: 13px;
                text-align: left;
            }

            QPushButton:hover {
                border: 1px solid #e3262e;
                background-color: #32373d;
            }
        """)

        self.language_menu = QMenu(
            self.language_button
        )

        self.language_menu.setStyleSheet("""
            QMenu {
                background-color: #292d32;
                color: #ffffff;
                border: 1px solid #3c4248;
                padding: 4px;
            }

            QMenu::item {
                padding: 7px 20px;
            }

            QMenu::item:selected {
                background-color: #e3262e;
            }
        """)

        languages = [
            ("fr", "Français", "fr.png"),
            ("en", "English", "gb.png"),
            ("de", "Deutsch", "de.png"),
            ("es", "Español", "es.png"),
            ("cz", "Čeština", "cz.png"),
            ("ch1", "简体中文", "ch1.png"),
            ("ch2", "繁體中文", "ch2.png"),
            ("hu", "Magyar", "hu.png"),
            ("it", "Italiano", "it.png"),
            ("jp", "日本語", "jp.png"),
            ("kr", "한국어", "kr.png"),
            ("pl", "Polski", "pl.png"),
            ("pt", "Português", "pt.png"),
            ("ru", "Русский", "ru.png"),
            ("uk", "Українська", "uk.png"),
        ]

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

        for language_code, language_name, flag_name in languages:

            action = QAction(
                QIcon(
                    str(flags_path / flag_name)
                ),
                language_name,
                self.language_menu
            )

            action.setData(
                language_code
            )

            action.triggered.connect(
                lambda checked=False, code=language_code:
                    self.change_language(code)
            )

            self.language_menu.addAction(
                action
            )

        self.language_button.setMenu(
            self.language_menu
        )

        language_layout.addWidget(
            self.language_button
        )

        main_layout.addLayout(
            language_layout
        )


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
        language
    ):

        translation_manager.set_language(
            language
        )

        game_localization_manager.set_language(
            language
        )

        language_names = {
            "fr": "Français",
            "en": "English",
            "de": "Deutsch",
            "es": "Español",
            "cz": "Čeština",
            "ch1": "简体中文",
            "ch2": "繁體中文",
            "hu": "Magyar",
            "it": "Italiano",
            "jp": "日本語",
            "kr": "한국어",
            "pl": "Polski",
            "pt": "Português",
            "ru": "Русский",
            "uk": "Українська",
        }

        self.language_button.setText(
            "🌐 " + language_names.get(
                language,
                language
            )
        )

        self.language_changed.emit(
            language
        )

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