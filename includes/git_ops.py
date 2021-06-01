import os
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Optional

from git.refs.remote import RemoteReference
from git import Repo
import git

# from git import Repo


@dataclass
class GitArgs:

    origin: Repo
    index: Repo
    git_url: str = None
    git_port: str = "443"
    git_path: str = "/tmp/git/backups"
    git_server: str = "gitea.wizznet.co.uk"
    git_proto: tuple = ("https", "http", "ssh")
    git_project: str = "testorg"
    git_repo_name: str = "testrepo"
    git_branch: str = "master"
    git_remote: str = "origin"
    git_commit_message: str = "This is a config backup commit."
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

    def init(self) -> None:
        try:
            # init local
            git.Repo.init(self.args.git_path)
            # get repo object
            self.repo = Repo(self.args.git_path)
        except Exception as e:
            print(f"unable to init exception: {e}")

    def remote_add(self) -> None:
        # git remote add
        try:
            # if no remote then create one
            if len(self.repo.remotes) < 1:
                self.repo.create_remote(self.args.git_remote, self.git_url)
        except Exception as e:
            print(f"Error {e}")
            pass

    def create_index(self) -> None:
        self.index = self.repo.index

    def files_add(self) -> None:
        # add files
        self.index.add("*")
        pass

    def commit(self) -> None:
        self.index.commit(self.args.git_commit_message)
        pass

    def fetch(self) -> None:
        # fetch --all
        # todo
        pass

    def set_remote_reference(self) -> None:
        # Setup remote tracking
        remote_ref = RemoteReference(
            self.repo,
            f"refs/remotes/{self.args.git_remote}/{self.args.git_branch}",
        )
        # set tracking branch
        self.repo.head.reference.set_tracking_branch(remote_ref)

        pass

    def push(self) -> None:

        try:
            # prepare push
            o = self.repo.remote(name=self.args.git_remote)
            # push to remote
            o.repo.remotes[0].push()

        except Exception as e:
            print(Exception(f"Cannot push to repo due to error: {e}"))
            pass

    def pull(self) -> None:
        try:
            o = self.repo.remote(name=self.args.git_remote)
            # pull from remote
            o.pull(self.args.git_remote, self.args.git_branch)
        except Exception as e:
            print(Exception(f"Cannot pull from repo due to error: {e}"))
            pass

    # create path
    def _create_local_path(self) -> None:
        # Create path
        from pathlib import Path

        return Path(self.args.git_path).mkdir(parents=True, exist_ok=True)

    def _check_local_path(self, path) -> bool:
        # does path exist
        return os.path.isdir(path)

    def _get_url_https(self) -> str:
        proto = self.args.git_proto[0]
        server = self.args.git_server
        port = self.args.git_port
        project = self.args.git_project
        repo = self.args.git_repo_name

        return str(f"{proto}://{server}:{port}/{project}/{repo}.git")

    def _get_url_gitea(self) -> str:
        proto = self.args.git_proto[1]
        server = self.args.git_server
        port = "3000"
        project = self.args.git_project
        repo = self.args.git_repo_name

        return str(f"{proto}://{server}:{port}/{project}/{repo}.git")

    def _get_url_ssh(self) -> str:
        prefix = "git"
        server = self.args.git_server
        project = self.args.git_project
        repo = self.args.git_repo_name

        return str(f"{prefix}@{server}/{project}/{repo}.git")

    def _generate_url(self) -> None:
        # generate url
        if self.server_type == "https":
            self.git_url = self._get_url_https()
        elif self.server_type == "gitea":
            self.git_url = self._get_url_gitea()
        elif self.server_type == "ssh":
            self.git_url = self._get_url_ssh()

    def setup_fs_paths(self, git_path: Optional[str]) -> None:
        if git_path is not None:
            self.git.args.git_path = git_path
        # does path exist?  if not then create it
        if not self.git.test_check_local_path(path=self.git.args.git_path):
            # create path
            self.git.test_create_local_path()
        return
