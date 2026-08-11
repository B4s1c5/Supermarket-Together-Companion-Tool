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

        if not self.is_dev():
            return

        if self.is_external_console():
            return

        env = os.environ.copy()

        env[
            self.environment_key
        ] = "1"

        script_path = Path(
            script_path
        ).resolve()

        src_path = (
            Path(__file__)
            .resolve()
            .parent
            .parent
        )

        project_root = (
            src_path
            .parent
        )

        current_pythonpath = env.get(
            "PYTHONPATH",
            ""
        )

        if current_pythonpath:

            env[
                "PYTHONPATH"
            ] = (
                str(src_path)
                + os.pathsep
                + current_pythonpath
            )

        else:

            env[
                "PYTHONPATH"
            ] = str(
                src_path
            )

        subprocess.Popen(
            [
                sys.executable,
                str(
                    script_path
                ),
                *sys.argv[1:],
            ],
            
            cwd=str(
                project_root
            ),
            env=env,
            creationflags=(
                subprocess.CREATE_NEW_CONSOLE
            ),
            #creationflags=0,
        )

        sys.exit(0)


dev_console = DevConsole()