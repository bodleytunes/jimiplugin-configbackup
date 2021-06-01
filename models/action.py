# from plugins.batfish.includes.helpers import generate_new_dict
from core.models import action
from core import auth, helpers

from git import Repo


from plugins.configbackup.includes.base import ConfigBackupArgs
from plugins.configbackup.includes.connect import ConnectArgs, Connect

from plugins.configbackup.includes.fortigate import (
    FortigateConnect,
    FortigateConnectArgs,
    FortigateConfigBackup,
    FortigateConfigBackupArgs,
)

from plugins.configbackup.includes.git_ops import GitOps as Git
from plugins.configbackup.includes.git_ops import GitArgs


class _cfgBackupConnect(action._action):
    # base vars
    host = str()
    device_hostname = str()
    device_model = str()
    port: int = 22  # sane default of ssh
    timeout: int = 60  # Sane default of 60s
    max_recv_time: int = 120

    def doAction(self, data) -> dict:

        # setup base args
        connect_args = ConnectArgs(
            host=self.host,
            port=self.port,
            timeout=self.timeout,
            max_recv_time=self.max_recv_time,
            device_hostname=self.device_hostname,
            device_model=self.device_model,
        )

        # pass connect_args object to event stream so available to other plugin flows e.g. fortigate action below
        data["eventData"]["args"] = {}
        data["eventData"]["args"] = {"connect_args": connect_args}
        # Model Details
        data["eventData"]["model"] = {}
        data["eventData"]["model"] = {"device_model": self.device_model}

        return {"result": True, "rc": 0, "msg": "Initiated Connection Args"}

    # data["eventData"]["args"] = {"connect_args": "hello world!"}

    def setAttribute(self, attr, value, sessionData=None) -> super:
        # set parent class session data
        return super(_cfgBackupConnect, self).setAttribute(
            attr, value, sessionData=sessionData
        )


class _cfgBackupFortigateConnect(action._action):

    # forti vars
    username = str()
    password = str()

    def doAction(self, data) -> dict:

        if self.password.startswith("ENC"):
            self.password = auth.getPasswordFromENC(self.password)
        else:
            self.password = ""

        connect_args = data["eventData"]["args"]["connect_args"]

        # setup forti args
        forti_connect_args = FortigateConnectArgs(
            username=self.username, password=self.password
        )

        # Create connection client instance

        # setup forti args
        forti_connect_args = FortigateConnectArgs(
            username=self.username, password=self.password
        )

        # Create connection instance
        client = FortigateConnect(
            connect_args=connect_args, forti_connect_args=forti_connect_args
        )

        if client is not None:
            data["eventData"]["remote"] = {}
            data["eventData"]["remote"] = {"client": client}
            return {"result": True, "rc": 0, "msg": "Success! Paramiko Client Created"}

        else:
            return {
                "result": False,
                "rc": 403,
                "msg": "Connection failed - {0}".format(client.error),
            }

    def setAttribute(self, attr, value, sessionData=None) -> super:
        if attr == "password" and not value.startswith("ENC "):
            self.password = "ENC {0}".format(auth.getENCFromPassword(value))
            return True
        # set parent class session data
        return super(_cfgBackupFortigateConnect, self).setAttribute(
            attr, value, sessionData=sessionData
        )


class _cfgBackupSave(action._action):
    command = str()
    timeout: int = 60

    dst_folder: str = "/tmp/gitbackup"

    def doAction(self, data) -> dict:

        # Add dest folder to eventData
        data["eventData"]["backup_args"] = {}
        data["eventData"]["backup_args"] = {"dst_folder": self.dst_folder}

        device_model = data["eventData"]["model"]["device_model"]

        # Setup Config related Args
        config_backup_args = ConfigBackupArgs(dst_folder=self.dst_folder)

        try:
            client = data["eventData"]["remote"]["client"]
        except KeyError:
            client = None
        # set dest folder sane defaults
        if self.dst_folder is None or self.dst_folder == "":
            self.dst_folder = "/tmp"

        if client:

            if device_model.upper() == "FORTIGATE":

                # Setup Fortigate connection related Args
                backup_args = FortigateConfigBackupArgs(
                    command=self.command,
                    timeout=self.timeout,
                )
                # Setup Fortigate related Args
                config_backup = FortigateConfigBackup(
                    client=client,
                    config_backup_args=config_backup_args,
                    backup_args=backup_args,
                )

            # Run config backup
            exitCode, errors = config_backup.download_config()

            if exitCode == 0:
                return {
                    "result": True,
                    "rc": exitCode,
                    "msg": "Command successfull",
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

    def setAttribute(self, attr, value, sessionData=None) -> super:
        # set parent class session data
        return super(_cfgBackupSave, self).setAttribute(
            attr, value, sessionData=sessionData
        )


class _cfgGitOps(action._action):

    git_port: str = str()
    # git_path
    git_path: str = "/tmp/git/backups"
    git_server: str = "gitea.company.com"
    git_port: str = "443"
    git_project: str = "my-project"
    git_repo_name: str = "backup-repo"
    git_branch: str = "master"
    git_remote: str = "origin"
    git_commit_message: str = "Jimi configuration backup commit."
    git_server_type: str = "gitea"

    git: Git

    def doAction(self, data) -> dict:
        # set the git path to the previously set destination folder if no explicit git path was passed in
        if data["eventData"]["backup_args"]["dst_folder"] is not None:
            if self.git_path is None or self.git_path == "/tmp/git/backups":
                self.git_path = data["eventData"]["backup_args"]["dst_folder"]

        # setup arguments
        args = self._setup_args()
        # run git operations
        git = Git(args)
        try:
            git.setup_fs_paths()
            git.init()
            git.remote_add()
            git.create_index()
            git.files_add()
            git.commit()
            git.set_remote_reference()
            git.push()
            git.pull()

            # put git object into eventData for further use?
            data["eventData"]["git"] = {}
            data["eventData"]["git"] = git

            return {
                "result": True,
                "rc": 0,
                "msg": "Git-Ops successfull",
                "data": "Git Operations Complete!",
                "errors": "",
            }
        except Exception as e:
            return {
                "result": False,
                "rc": 255,
                "msg": f"Git exception: {e}",
                "data": "",
                "errors": e,
            }

    def _setup_args(self) -> GitArgs:

        args = GitArgs(
            git_port=self.git_port,
            git_path=self.git_path,
            git_server=self.git_server,
            git_project=self.git_project,
            git_repo_name=self.git_repo_name,
            git_branch=self.git_branch,
            git_remote=self.git_remote,
            git_commit_message=self.git_commit_message,
            git_server_type=self.git_server_type,
        )

        return args

    def setAttribute(self, attr, value, sessionData=None) -> super:
        # set parent class session data
        return super(_cfgGitOps, self).setAttribute(
            attr, value, sessionData=sessionData
        )
