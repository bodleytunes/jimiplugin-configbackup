# from plugins.batfish.includes.helpers import generate_new_dict
from core.models import action
from core import auth, helpers

import jimi

from plugins.configbackup.includes.base.core import (
    FortigateConnect,
    ConnectArgs,
    FortigateConnectArgs,
)
from plugins.configbackup.includes.base.config import (
    FortigateConfigBackup,
    FortigateConfigBackupArgs,
)


class _cfgBackupConnect(action._action):
    # base vars
    host = str()
    device_hostname = str()
    port = int()
    timeout = int()
    max_recv_time = int()
    # forti vars
    username = str()
    password = str()

    client: FortigateConnect

    def doAction(self, data):
        if self.password.startswith("ENC"):
            password = auth.getPasswordFromENC(self.password)
        else:
            password = ""
        # setup base args
        connect_args = ConnectArgs(
            host=self.host,
            port=self.port,
            timeout=self.timeout,
            max_recv_time=self.max_recv_time,
            device_hostname=self.device_hostname,
        )
        # setup forti args
        forti_connect_args = FortigateConnectArgs(
            username=self.username, password=password
        )

        # Create connection instance
        client = FortigateConnect(
            connect_args=connect_args, forti_connect_args=forti_connect_args
        )

        if client is not None:
            data["eventData"]["remote"] = {}
            data["eventData"]["remote"] = {"client": client}
            return {"result": True, "rc": 0, "msg": "Connection Successful"}
        else:
            return {
                "result": False,
                "rc": 403,
                "msg": "Connection failed - {0}".format(client.error),
            }

    def setAttribute(self, attr, value, sessionData=None):
        if attr == "password" and not value.startswith("ENC "):
            self.password = "ENC {0}".format(auth.getENCFromPassword(value))
            return True
        # set parent class session data
        return super(_cfgBackupConnect, self).setAttribute(
            attr, value, sessionData=sessionData
        )


class _cfgBackupSave(action._action):
    command = str()
    timeout = 60
    dst_folder = str()
    device_model = str()

    def doAction(self, data):

        backup_args = FortigateConfigBackupArgs(
            command=self.command,
            timeout=self.timeout,
            dst_folder=self.dst_folder,
            device_model=self.device_model,
        )

        try:
            client = data["eventData"]["remote"]["client"]
        except KeyError:
            client = None
        # set dest folder sane defaults
        if self.dst_folder is None or self.dst_folder == "":
            self.dst_folder = "/tmp"

        if client:

            config_backup = FortigateConfigBackup(
                client=client, backup_args=backup_args
            )

            exitCode, errors = config_backup.download_config()

            if exitCode is None:
                return {
                    "result": True,
                    "rc": exitCode,
                    "msg": "Command succesfull",
                    "data": "config saved!",
                    "errors": errors,
                }
            else:
                return {
                    "result": False,
                    "rc": 255,
                    "msg": client.error,
                    "data": "",
                    "errors": "",
                }
        else:
            return {"result": False, "rc": 403, "msg": "No connection found"}

    def setAttribute(self, attr, value, sessionData=None):
        # set parent class session data
        return super(_cfgBackupSave, self).setAttribute(
            attr, value, sessionData=sessionData
        )
