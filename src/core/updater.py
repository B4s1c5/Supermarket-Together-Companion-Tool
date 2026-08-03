import tempfile
import requests
import subprocess
import sys


from pathlib import Path
from PySide6.QtCore import QObject, Signal, Slot



def download_update(download_url):
    temp_dir = Path(tempfile.mkdtemp(prefix="supermarket_update_"))
    zip_path = temp_dir / "update.zip"

    response = requests.get(
        download_url,
        stream=True,
        timeout=30
    )
    response.raise_for_status()

    with open(zip_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)

    return zip_path


class DownloadWorker(QObject):

    finished = Signal(object)
    error = Signal(str)

    def __init__(self, download_url):
        super().__init__()
        self.download_url = download_url

    @Slot()
    def run(self):
        try:
            zip_path = download_update(self.download_url)
            self.finished.emit(zip_path)

        except Exception as error:
            self.error.emit(str(error))


def launch_updater(zip_path):
    if not getattr(sys, "frozen", False):
        raise RuntimeError(
            "L'installation automatique ne peut être lancée "
            "que depuis la version EXE."
        )

    install_dir = Path(sys.executable).resolve().parent
    exe_name = Path(sys.executable).name

    updater_exe = install_dir / "Updater.exe"

    if not updater_exe.exists():
        raise FileNotFoundError(
            f"Updater.exe introuvable : {updater_exe}"
        )

    subprocess.Popen(
        [
            str(updater_exe),
            str(zip_path),
            str(install_dir),
            exe_name,
        ],
        cwd=str(install_dir),
    )