from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
)


class ModuleCard(QFrame):

    clicked = Signal()

    def __init__(
        self,
        icon,
        title,
        description,
        parent=None
    ):
        super().__init__(parent)

        self.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.setMinimumHeight(140)

        self.setStyleSheet("""
            ModuleCard {
                background-color: #292d32;
                border: 1px solid #3c4248;
                border-radius: 14px;
            }

            ModuleCard:hover {
                background-color: #32373d;
                border: 1px solid #e3262e;
            }
        """)

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            25,
            20,
            25,
            20
        )

        layout.setSpacing(10)

        # -------------------------
        # Titre
        # -------------------------

        self.title_label = QLabel(
            f"{icon}   {title}"
        )

        self.title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: 600;
            color: #ffffff;
            border: none;
            background: transparent;
        """)

        # -------------------------
        # Description
        # -------------------------

        self.description_label = QLabel(
            description
        )

        self.description_label.setWordWrap(
            True
        )

        self.description_label.setStyleSheet("""
            font-size: 14px;
            color: #c7cbd1;
            border: none;
            background: transparent;
        """)

        layout.addWidget(
            self.title_label
        )

        layout.addWidget(
            self.description_label
        )

        layout.addStretch()


    def mousePressEvent(self, event):

        if (
            event.button()
            == Qt.MouseButton.LeftButton
        ):
            self.clicked.emit()

        super().mousePressEvent(event)