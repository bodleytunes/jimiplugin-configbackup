from dataclasses import dataclass

import os
from pathlib import Path

from .core import FortigateConnect


@dataclass
class FortigateConfigBackupArgs:

    command: str
    dst_folder: str
    timeout: int
    device_model: str


class FortigateConfigBackup:

    client: FortigateConnect

    def __init__(
        self,
        client: FortigateConnect = None,
        backup_args: FortigateConfigBackupArgs = None,
    ) -> None:

        self._backup_args = backup_args

    def download_config(self, command, timeout=None, dstFolder=None):
        # todo - WIP
        self.client.channel.send("{0}{1}".format(self._backup_args.command, "\n"))
        # receive config
        output = self.client.recv()
        # create dirs
        Path(self._backup_args.dst_folder).mkdir(parents=True, exist_ok=True)
        # create file
        file = open(
            os.path.join(
                self._backup_args.dst_folder,
                f"{self.client._connect_args.device_hostname}-{self.client._connect_args.host}.cfg",
            ),
            "w",
        )
        file.write(output)
        file.close()
        return (0, "")
