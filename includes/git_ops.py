import os
from dataclasses import dataclass
from abc import ABC, abstractmethod

from git.refs.remote import RemoteReference
from git import Repo
import git

# from git import Repo


@dataclass
class GitArgs:

    origin: Repo
    index: Repo
    git_url: str = None
    git_host: str = None
    git_port: str = "443"
    git_path: str = "/tmp/git/backups"
    git_server: str = "gitea.wizznet.co.uk"
    git_proto: tuple = ("https", "http", "ssh")
    git_project: str = "testorg"
    git_repo_name: str = "testrepo"
    git_branch: str = "master"
    git_remote: str = "testrepo"
    command_type: tuple = ("CLONE", "FETCH")
    server_type: str = "gitea"


class BaseGitOps(ABC):
    pass

    @abstractmethod
    def clone():
        pass

    @abstractmethod
    def fetch():
        pass

    @abstractmethod
    def commit():
        pass

    @abstractmethod
    def push():
        pass


class GitOps(BaseGitOps):
    def __init__(self, args: GitArgs = None) -> None:
        super().__init__()

        self.git_args = args

        self._generate_url()

    pass

    def clone(self):
        # todo
        pass

    def init(self):
        try:
            self.repo = git.Repo.init(self.args.git_path)
        except Exception as e:
            print(f"unable to init exception: {e}")
            self.repo = Repo(self.args.git_path)
            self.origin = self.repo.remote(name=self.args.git_remote)

    def remote_add(self):
        # git remote add
        try:
            if not self.origin.repo.head:
                self.origin = self.origin.create_remote(
                    self.args.git_repo_name, self.git_url
                )
        except Exception as e:
            print(f"Error {e}")

            pass

    def create_index(self):
        self.index = self.repo.index

    def files_add(self):
        # add files
        self.index.add("*")
        pass

    def commit(self):
        self.index.commit("commit message")
        pass

    def fetch(self):
        # fetch --all
        # todo
        pass

    def set_remote_reference(self):
        # Setup remote tracking
        remote_ref = RemoteReference(
            self.repo,
            f"refs/remotes/{self.args.git_repo_name}/{self.args.git_branch}",
        )
        self.repo.head.reference.set_tracking_branch(remote_ref)

        pass

    def push(self):

        try:
            # prepare push
            o = self.repo.remote(name=self.args.git_remote)
            # push to remote
            o.repo.remotes[0].push()

        except Exception as e:
            print(Exception(f"Cannot push to repo due to error: {e}"))
            pass

    def pull(self):
        try:
            o = self.repo.remote(name=self.args.git_remote)
            # pull from remote
            o.pull(self.args.git_remote, self.args.git_branch)
        except Exception as e:
            print(Exception(f"Cannot pull from repo due to error: {e}"))
            pass

    # create path
    def create_local_path(self):
        # Create path
        from pathlib import Path

        return Path(self.args.git_path).mkdir(parents=True, exist_ok=True)

    def check_local_path(self, path):
        # does path exist
        return os.path.isdir(path)

    def _get_url_https(self):
        proto = self.args.git_proto[0]
        server = self.args.git_server
        port = self.args.git_port
        project = self.args.git_project
        repo = self.args.git_repo_name

        return str(f"{proto}://{server}:{port}/{project}/{repo}.git")

    def _get_url_gitea(self):
        proto = self.args.git_proto[1]
        server = self.args.git_server
        port = "3000"
        project = self.args.git_project
        repo = self.args.git_repo_name

        return str(f"{proto}://{server}:{port}/{project}/{repo}.git")

    def _get_url_ssh(self):
        prefix = "git"
        server = self.args.git_server
        project = self.args.git_project
        repo = self.args.git_repo_name

        return str(f"{prefix}@{server}/{project}/{repo}.git")

    def _generate_url(self):
        # generate url
        if self.server_type == "https":
            self.git_url = self._get_url_https()
        elif self.server_type == "gitea":
            self.git_url = self._get_url_gitea()
        elif self.server_type == "ssh":
            self.git_url = self._get_url_ssh()
