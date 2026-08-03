import requests

from PySide6.QtCore import QObject, Signal, Slot
from version import APP_VERSION


GITHUB_API_URL = (
    "https://api.github.com/repos/"
    "B4s1c5/Supermarket-Together-Companion-Tool/releases/latest"
)


def check_for_update():
    try:
        response = requests.get(
            GITHUB_API_URL,
            timeout=5
        )
        response.raise_for_status()

        release = response.json()

        download_url = None

        for asset in release.get("assets", []):
            if asset["name"].endswith("-Windows.zip"):
                download_url = asset["browser_download_url"]
                break

        latest_version = release["tag_name"].lstrip("v")

        current = tuple(
            int(number)
            for number in APP_VERSION.split(".")
        )

        latest = tuple(
            int(number)
            for number in latest_version.split(".")
        )

        if latest > current:
            return {
                "available": True,
                "version": latest_version,
                "url": release["html_url"],
                "download_url": download_url,
            }

        return {
            "available": False,
            "version": latest_version,
            "url": None,
            "download_url": None,
        }

    except Exception as error:

        print(f"Erreur update checker : {error}")

        # Une erreur réseau ne doit jamais empêcher
        # l'application de démarrer.
        return {
            "available": False,
            "version": None,
            "url": None,
            "download_url": None,
        }


class UpdateWorker(QObject):

    finished = Signal(dict)

    @Slot()
    def run(self):
        result = check_for_update()
        self.finished.emit(result)