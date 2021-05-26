import time
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any, Callable
import re, os
from pathlib import Path

from paramiko import SSHClient, AutoAddPolicy


@dataclass
class BaseConfigBackupArgs:

    pass


class BaseConfigBackup(ABC):
    def __init__(self, base_config_backup_args: BaseConfigBackupArgs = None) -> None:
        super().__init__()
        self._base_config_backup_args = base_config_backup_args

    def save_config(self):
        pass

    @abstractmethod
    def connect(self):
        pass


@dataclass
class ConfigBackupArgs:

    save_path: str


class ConfigBackup(BaseConfigBackup):
    def __init__(self, config_backup_args: ConfigBackupArgs) -> None:
        super().__init__()
        self._config_backup_args = config_backup_args

    def save_config(self):
        pass


@dataclass
class ConnectArgs:

    host: str
    device_hostname: str
    port: int
    timeout: int
    max_recv_time: int


class Connect(BaseConfigBackup):
    def __init__(self, connect_args: ConnectArgs = None) -> None:

        self.error: str = None
        self.connect_args = connect_args

    @abstractmethod
    def connect(self):
        pass


@dataclass
class FortigateConnectArgs:

    username: str
    password: str

    vdom: str = "root"


class FortigateConnect(Connect):
    def __init__(
        self,
        forti_connect_args: FortigateConnectArgs = None,
        connect_args: ConnectArgs = None,
    ) -> None:

        # instanciate super/parent variables
        super().__init__(connect_args=connect_args)

        self.forti_connect_args = forti_connect_args
        self.channel = None
        self.client = None

        self.client = self.connect()

    def connect(self):
        try:
            client = SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(AutoAddPolicy())

            client.connect(
                hostname=self.connect_args.host,
                username=self.forti_connect_args.username,
                password=self.forti_connect_args.password,
                timeout=self.connect_args.timeout,
                look_for_keys=True,
            )

            self.channel = client.invoke_shell()

            detectedDevice = (
                self.channel.recv(len(self.connect_args.device_hostname) + 2)
                .decode()
                .strip()
            )
            if detectedDevice != "{0} #".format(
                self.connect_args.device_hostname
            ) and detectedDevice != "{0} $".format(self.connect_args.device_hostname):
                self.error = (
                    "Device detected name does not match the device name provided."
                )
                self.disconnect
                return None

            return client
        except Exception as e:
            self.error = e
            return None

    def disconnect(self):
        if self.client:
            self.client.close()
            self.client = None

    def recv(self):
        startTime = time.time()
        recvBuffer = ""

        while time.time() - startTime < self.connect_args.max_recv_time:

            if self.channel.recv_ready():
                recvBuffer += self.channel.recv(1024).decode().strip()

                if recvBuffer.split("\n")[-1] == "--More--":
                    self.channel.send(" ")
                    recvBuffer = recvBuffer[:-8]
                elif re.match(
                    r"^{0} ((#|\$)|\([a-z]+\) (#|\$))$".format(
                        self.connect_args.device_hostname
                    ),
                    recvBuffer.split("\n")[-1],
                ):
                    break
            time.sleep(0.1)
        return recvBuffer

    def __del__(self):
        self.disconnect()
