import sys
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Slot
from PySide6.QtWidgets import QApplication, QMessageBox

from ui.main_window import MainWindow
from core.update_checker import UpdateWorker
from core.updater import DownloadWorker


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent.parent

    return base_path / relative_path


class UpdateHandler(QObject):

    def __init__(self, window):
        super().__init__(window)
        self.window = window

    @Slot(dict)
    def handle_update(self, info):
        if not info["available"]:
            return

        message = QMessageBox(self.window)
        message.setWindowTitle("Mise à jour disponible")
        message.setIcon(QMessageBox.Information)

        message.setText(
            f"Une nouvelle version ({info['version']}) est disponible."
        )

        message.setInformativeText(
            "Voulez-vous télécharger la mise à jour maintenant ?"
        )

        message.setStandardButtons(
            QMessageBox.Yes | QMessageBox.No
        )

        message.button(QMessageBox.Yes).setText("Mettre à jour")
        message.button(QMessageBox.No).setText("Plus tard")

        result = message.exec()

        if result == QMessageBox.Yes:
            self.start_download(info["download_url"])

    def start_download(self, download_url):
        if not download_url:
            QMessageBox.warning(
                self.window,
                "Mise à jour",
                "Le fichier de mise à jour est introuvable."
            )
            return

        self.download_thread = QThread()
        self.download_worker = DownloadWorker(download_url)

        self.download_worker.moveToThread(
            self.download_thread
        )

        self.download_thread.started.connect(
            self.download_worker.run
        )

        self.download_worker.finished.connect(
            self.download_finished
        )

        self.download_worker.error.connect(
            self.download_error
        )

        self.download_worker.finished.connect(
            self.download_thread.quit
        )

        self.download_worker.error.connect(
            self.download_thread.quit
        )

        self.download_thread.finished.connect(
            self.download_worker.deleteLater
        )

        self.download_thread.finished.connect(
            self.download_thread.deleteLater
        )

        self.download_thread.start()

    @Slot(object)
    def download_finished(self, zip_path):
        QMessageBox.information(
            self.window,
            "Mise à jour téléchargée",
            (
                "La mise à jour a été téléchargée "
                f"avec succès.\n\n{zip_path}"
            )
        )

    @Slot(str)
    def download_error(self, error):
        QMessageBox.critical(
            self.window,
            "Erreur de mise à jour",
            (
                "Impossible de télécharger "
                f"la mise à jour.\n\n{error}"
            )
        )

def main():
    app = QApplication(sys.argv)

    style_path = resource_path("src/ui/style.qss")

    with open(style_path, "r", encoding="utf-8") as file:
        app.setStyleSheet(file.read())

    window = MainWindow()
    window.show()
    update_handler = UpdateHandler(window)

    # Vérification des mises à jour en arrière-plan
    update_thread = QThread()
    update_worker = UpdateWorker()

    update_worker.moveToThread(update_thread)

    update_thread.started.connect(update_worker.run)

    update_worker.finished.connect(
        update_handler.handle_update
    )

    update_worker.finished.connect(update_thread.quit)
    update_worker.finished.connect(update_worker.deleteLater)
    update_thread.finished.connect(update_thread.deleteLater)

    # On garde les références en vie
    window.update_thread = update_thread
    window.update_worker = update_worker
    window.update_handler = update_handler

    update_thread.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()