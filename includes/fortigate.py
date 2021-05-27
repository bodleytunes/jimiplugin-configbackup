from dataclasses import dataclass
import os, re
from pathlib import Path
import time

from paramiko import SSHClient, AutoAddPolicy

from plugins.configbackup.includes.base import ConfigBackupArgs
from plugins.configbackup.includes.connect import Connect, ConnectArgs


@dataclass
class FortigateConfigBackupArgs:

    command: str
    timeout: int


@dataclass
class FortigateConnectArgs:

    username: str
    password: str

    vdom: str = "root"


class FortigateConnect(Connect):
    def __init__(
        self,
        connect_args: ConnectArgs = None,
        forti_connect_args: FortigateConnectArgs = None,
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


class FortigateConfigBackup:

    client: FortigateConnect

    def __init__(
        self,
        client: FortigateConnect = None,
        backup_args: FortigateConfigBackupArgs = None,
        config_backup_args: ConfigBackupArgs = None,
    ) -> None:

        self.client = client
        self._backup_args = backup_args
        self._config_backup_args = config_backup_args

    def download_config(self):

        self.client.channel.send("{0}{1}".format(self._backup_args.command, "\n"))
        # receive config
        output = self.client.recv()
        # create dirs
        Path(self._config_backup_args.dst_folder).mkdir(parents=True, exist_ok=True)
        # create file
        file = open(
            os.path.join(
                self._config_backup_args.dst_folder,
                f"{self.client.connect_args.device_hostname}-{self.client.connect_args.host}.cfg",
            ),
            "w",
        )
        file.write(output)
        file.close()
        return (0, "")
