import os
import subprocess
import sys

from pathlib import Path


class DevConsole:

    def __init__(self):

        self.environment_key = (
            "SMT_DEV_CONSOLE"
        )

    def is_dev(self):

        return not getattr(
            sys,
            "frozen",
            False
        )

    def is_external_console(self):

        return (
            os.getenv(
                self.environment_key
            )
            == "1"
        )

    def open(
        self,
        script_path
    ):

        return


dev_console = DevConsole()