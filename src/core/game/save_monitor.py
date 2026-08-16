import re

from pathlib import Path

from PySide6.QtCore import (
    QObject,
    QTimer,
    Signal,
)


class SaveMonitor(QObject):

    save_loaded = Signal(
        int,
        str,
        object,
        object,
    )

    def __init__(
        self,
        save_directory=None,
        parent=None,
    ):
        super().__init__(
            parent
        )

        if save_directory is None:

            save_directory = (
                Path.home()
                / "AppData"
                / "LocalLow"
                / "DDTNL"
                / "Supermarket Together"
            )

        self.save_directory = Path(
            save_directory
        )

        self.timer = QTimer(
            self
        )

        self.timer.setInterval(
            500
        )

        self.timer.timeout.connect(
            self.check_saves
        )

        self.known_files = {}

        self.current_slot = None
        self.current_save_file = None
        self.current_day_file = None
        self.current_day = None


    def start(self):

        self.save_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        self.known_files = (
            self.get_main_save_states()
        )

        self.timer.start()


    def stop(self):

        self.timer.stop()


    def get_main_save_states(self):

        states = {}

        if not self.save_directory.exists():

            return states

        pattern = re.compile(
            r"^StoreFile(\d+)\.es3$"
        )

        for path in self.save_directory.iterdir():

            if not path.is_file():

                continue

            match = pattern.match(
                path.name
            )

            if match is None:

                continue

            slot = int(
                match.group(1)
            )

            try:

                states[slot] = (
                    path.stat().st_mtime_ns,
                    path.stat().st_size,
                )

            except OSError:

                continue

        return states


    def check_saves(self):

        current_files = (
            self.get_main_save_states()
        )

        changed_slots = []

        for slot, state in current_files.items():

            previous_state = (
                self.known_files.get(
                    slot
                )
            )

            if (
                previous_state is not None
                and state != previous_state
            ):

                changed_slots.append(
                    slot
                )

        self.known_files = current_files

        if not changed_slots:

            return

        slot = changed_slots[-1]

        self.process_loaded_save(
            slot
        )


    def process_loaded_save(
        self,
        slot,
    ):

        save_file = (
            self.save_directory
            / f"StoreFile{slot}.es3"
        )

        day_file, day = (
            self.find_latest_day_file(
                slot
            )
        )

        self.current_slot = slot
        self.current_save_file = (
            save_file
        )
        self.current_day_file = (
            day_file
        )
        self.current_day = day

        self.save_loaded.emit(
            slot,
            str(save_file),
            str(day_file)
            if day_file is not None
            else None,
            day,
        )


    def find_latest_day_file(
        self,
        slot,
    ):

        pattern = re.compile(
            rf"^StoreFile{slot}Day(\d+)\.es3$"
        )

        latest_file = None
        latest_day = None

        if not self.save_directory.exists():

            return None, None

        for path in self.save_directory.iterdir():

            if not path.is_file():

                continue

            match = pattern.match(
                path.name
            )

            if match is None:

                continue

            day = int(
                match.group(1)
            )

            if (
                latest_day is None
                or day > latest_day
            ):

                latest_day = day
                latest_file = path

        return latest_file, latest_day
    