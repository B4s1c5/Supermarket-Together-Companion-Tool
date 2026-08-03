import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    with open("src/ui/style.qss", "r", encoding="utf-8") as file:
        app.setStyleSheet(file.read())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()