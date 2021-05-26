# from plugins.batfish.includes.helpers import generate_new_dict
from core.models import action
from core import auth, helpers

from plugins.configbackup.includes.base.core import (
    FortigateConnect,
    ConnectArgs,
    FortigateConnectArgs,
)
from plugins.batfish.includes.queries.access_check import AccessCheck
from plugins.batfish.includes.queries.trace_route_check import TraceRouteCheck
from plugins.batfish.includes.queries.reachability_check import ReachabilityCheck

# from plugins.batfish.includes.queries.ip_owners import IpOwnersCheck
# from plugins.batfish.includes.queries.node_properties import NodePropertiesCheck


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

    # setup base args
    connect_args = ConnectArgs(
        host=host, port=port, timeout=timeout, max_recv_time=max_recv_time
    )
    # setup forti args
    forti_connect_args = FortigateConnectArgs(username=username, password=password)

    def doAction(self, data):

        # Create connection instance
        client = FortigateConnect(self.connect_args, self.forti_connect_args)

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
        try:
            client = data["eventData"]["remote"]["client"]
        except KeyError:
            client = None
        # set dest folder sane defaults
        if self.dstFolder is None or self.dstFolder == "":
            self.dstFolder = "/tmp"
        if client:
            exitCode, errors = client.download_config(
                command=self.command,
                timeout=self.timeout,
                dstFolder=self.dstFolder,
            )

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
