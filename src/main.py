import sys
import os
import subprocess
import ctypes

from pathlib import Path

from core.dev_console import dev_console

from PySide6.QtCore import(
    QObject, 
    QThread, 
    Slot,
    QTimer,
)
from PySide6.QtWidgets import(
    QApplication, 
    QMessageBox,
)

from ui.main_window import MainWindow
from core.update_checker import UpdateWorker
from core.updater import(
    DownloadWorker, 
    launch_updater,
)


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
        try:
            launch_updater(zip_path)

        except Exception as error:
            QMessageBox.critical(
                self.window,
                "Erreur de mise à jour",
                (
                    "Impossible de lancer l'installation "
                    f"de la mise à jour.\n\n{error}"
                )
            )
            return

        QApplication.quit()

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


class StartupProgress:

    def __init__(self):

        self.steps = [
            "Initialisation Qt",
            "Chargement du thème",
            "Chargement des données",
            "Traductions",
            "Construction de l'interface",
            "Finalisation",
        ]

        self.current_step = 0

    def start(self):

        if getattr(
            sys,
            "frozen",
            False
        ):
            return

        os.system(
            "cls"
        )

        print(
            "SMT Companion - Demarrage\n"
        )

        self.display(
            self.steps[0]
        )

    def next(
        self,
        message
    ):

        if getattr(
            sys,
            "frozen",
            False
        ):
            return

        self.current_step = min(
            self.current_step + 1,
            len(self.steps)
        )

        print(
            "\r"
            + " " * 100
            + "\r",
            end="",
            flush=True
        )

        print(
            f"[OK] {message}"
        )

        next_message = (
            self.steps[
                self.current_step
            ]
            if self.current_step < len(
                self.steps
            )
            else "Pret"
        )

        self.display(
            next_message
        )

    def display(
        self,
        message
    ):

        total = len(
            self.steps
        )

        percent = int(
            self.current_step
            / total
            * 100
        )

        width = 30

        filled = int(
            width
            * percent
            / 100
        )

        bar = (
            "#" * filled
            + "-" * (
                width - filled
            )
        )

        print(
            f"\r[GLOBAL] [{bar}] "
            f"{percent:3d}%  "
            f"{message}",
            end="",
            flush=True
        )

    def finish(self):

        if getattr(
            sys,
            "frozen",
            False
        ):
            return

        self.current_step = len(
            self.steps
        )

        print(
            "\r"
            + " " * 100
            + "\r",
            end="",
            flush=True
        )

        self.display(
            "Pret"
        )

        print()

startup_progress = StartupProgress()


def hide_dev_console():

    if getattr(
        sys,
        "frozen",
        False
    ):
        return

    if os.getenv(
        "SMT_DEV_CONSOLE"
    ) != "1":
        return

    console_window = (
        ctypes.windll.kernel32
        .GetConsoleWindow()
    )

    if console_window:

        ctypes.windll.user32.ShowWindow(
            console_window,
            0
        )


def focus_dev_console():

    if getattr(
        sys,
        "frozen",
        False
    ):
        return

    if os.getenv(
        "SMT_DEV_CONSOLE"
    ) != "1":
        return

    console_window = (
        ctypes.windll.kernel32
        .GetConsoleWindow()
    )

    if not console_window:
        return

    user32 = ctypes.windll.user32

    HWND_TOPMOST = -1
    SWP_NOMOVE = 0x0002
    SWP_NOSIZE = 0x0001

    user32.SetWindowPos(
        console_window,
        HWND_TOPMOST,
        0,
        0,
        0,
        0,
        SWP_NOMOVE
        | SWP_NOSIZE
    )


def main():

    dev_console.open(
        __file__
    )

    startup_progress.start()

    # -------------------------
    # Qt
    # -------------------------

    app = QApplication(
        sys.argv
    )

    startup_progress.next(
        "Qt initialise"
    )

    # -------------------------
    # Theme
    # -------------------------

    style_path = resource_path(
        "src/ui/style.qss"
    )

    with open(
        style_path,
        "r",
        encoding="utf-8"
    ) as file:

        app.setStyleSheet(
            file.read()
        )

    startup_progress.next(
        "Theme charge"
    )

    # -------------------------
    # Interface + donnees + i18n
    # -------------------------

    startup_progress.next(
        "Chargement des donnees"
    )

    startup_progress.next(
        "Traductions et interface"
    )

    window = MainWindow()

    startup_progress.next(
        "Interface construite"
    )

    # -------------------------
    # Fin du démarrage
    # -------------------------

    startup_progress.finish()

    startup_progress.finish()

    def finish_startup():

        hide_dev_console()

        window.show()
        window.raise_()
        window.activateWindow()

    QTimer.singleShot(
        500,
        finish_startup
    )

    update_handler = UpdateHandler(
        window
    )

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