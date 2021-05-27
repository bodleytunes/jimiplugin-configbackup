from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any, Callable
import os
from pathlib import Path

from paramiko import SSHClient, AutoAddPolicy


@dataclass
class BaseConfigBackupArgs:

    pass


@dataclass
class BaseConnectArgs:

    pass


@dataclass
class ConfigBackupArgs:

    dst_folder: str


class BaseConnect(ABC):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def connect(self):
        pass


class BaseConfigBackup(ABC):
    def __init__(self, base_config_backup_args: BaseConfigBackupArgs = None) -> None:
        super().__init__()
        self._base_config_backup_args = base_config_backup_args


class ConfigBackup(BaseConfigBackup):
    def __init__(self, config_backup_args: ConfigBackupArgs) -> None:
        super().__init__()
        self._config_backup_args = config_backup_args

    def save_config(self):
        pass
