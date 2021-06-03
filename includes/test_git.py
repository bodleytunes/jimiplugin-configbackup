from dataclasses import dataclass
from abc import ABC, abstractmethod
from logging import exception
from git.refs.remote import RemoteReference
import pytest, pytest_mock, pytest_cov

import os, sys

PACKAGE_PARENT = "../../../"
SCRIPT_DIR = os.path.dirname(
    os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
)
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
from typing import Union
from unittest.mock import patch
from git import Repo
import git
import pytest


@dataclass
class Test_GitArgs:
    # http://gitea.wizznet.co.uk:3000/testorg/testrepo.git

    git_url: str = None
    git_port: str = "443"
    git_path: str = "/tmp/git/backups"
    git_server: str = "gitea.wizznet.co.uk"
    git_proto: tuple = ("https", "http", "ssh")
    git_project: str = "testorg"
    git_repo_name: str = "testrepo"
    git_branch: str = "master"
    git_remote: str = "origin"
    git_server_type: str = "gitea"
    command_type: tuple = ("CLONE", "FETCH")


class Test_BaseGit(ABC):
    pass

    @abstractmethod
    def test_clone():
        pass

    @abstractmethod
    def test_fetch():
        pass

    @abstractmethod
    def test_commit():
        pass

    @abstractmethod
    def test_push():
        pass


class Test_Git(Test_BaseGit):
    git_port: str = None
    git_host: str = None
    git_path: str
    git_server: str
    git_repo_name: str
    origin: Repo
    index: Repo
    git_remote: str
    # git_server_type: tuple = ("https", "ssh", "gitea")
    git_server_type: str = "gitea"

    def __init__(self, args: Test_GitArgs = None) -> None:
        super().__init__()

        self.args = args
        self.git_remote = args.git_remote
        # generate url
        if self.git_server_type == "https":
            self.git_url = self._test_get_url_https()
        elif self.git_server_type == "gitea":
            self.git_url = self._test_get_url_gitea()
        elif self.git_server_type == "ssh":
            self.git_url = self._test_get_url_ssh()

    def test_init(self):
        try:
            # init local
            git.Repo.init(self.args.git_path)
            # get repo object
            self.repo = Repo(self.args.git_path)
        except Exception as e:
            print(f"unable to init exception: {e}")

    def test_remote_add(self):
        # git remote add
        try:
            # if no remote then create one
            if len(self.repo.remotes) < 1:
                self.repo.create_remote(self.args.git_remote, self.git_url)
        except Exception as e:
            print(f"Error {e}")
            pass

    def test_create_index(self):
        self.index = self.repo.index

    def test_files_add(self):
        # add files
        self.index.add("*")
        pass

    def test_commit(self):
        self.index.commit("commit message")
        pass

    def test_fetch(self):
        # fetch --all
        pass

    def test_set_remote_reference(self):
        # Setup remote tracking
        remote_ref = RemoteReference(
            self.repo,
            f"refs/remotes/{self.args.git_remote}/{self.args.git_branch}",
        )
        self.repo.head.reference.set_tracking_branch(remote_ref)

        pass

    def test_push(self):

        try:
            # prepare push
            o = self.repo.remote(name=self.args.git_remote)
            # push to remote
            o.repo.remotes[0].push(force=True)

        except Exception as e:
            print(Exception(f"Cannot push to repo due to error: {e}"))
            pass

    def test_pull(self):
        try:
            o = self.repo.remote(name=self.args.git_remote)
            # pull from remote
            o.pull(self.args.git_remote, self.args.git_branch)
        except Exception as e:
            print(Exception(f"Cannot pull from repo due to error: {e}"))
            pass

    # create path
    def test_create_local_path(self):
        # Create path
        from pathlib import Path

        return Path(self.args.git_path).mkdir(parents=True, exist_ok=True)

    def test_check_local_path(self, path):
        # does path exist
        return os.path.isdir(path)

    def _test_get_url_https(self):
        proto = self.args.git_proto[0]
        server = self.args.git_server
        port = self.args.git_port
        project = self.args.git_project
        repo = self.args.git_repo_name

        return str(f"{proto}://{server}:{port}/{project}/{repo}.git")

    def _test_get_url_gitea(self):
        proto = self.args.git_proto[1]
        server = self.args.git_server
        port = "3000"
        project = self.args.git_project
        repo = self.args.git_repo_name

        return str(f"{proto}://{server}:{port}/{project}/{repo}.git")

    def _test_get_url_ssh(self):
        prefix = "git"
        server = self.args.git_server
        project = self.args.git_project
        repo = self.args.git_repo_name

        return str(f"{prefix}@{server}/{project}/{repo}.git")

    def test_clone(
        self, local_clone_path: str, url_path: str, repo: git.Repo
    ) -> Union[git.Repo, bool]:
        # pre flights

        if self._check_local_path(path=local_clone_path):
            if self._check_repo_exists(path=local_clone_path):
                try:
                    self.repo = repo.clone_from(url=url_path, to_path="/tmp")
                    return self.repo
                except Exception as e:
                    print(f"can't clone repo: {e}")
                    return False
        else:
            try:
                self.repo = repo.clone(path=url_path)
                return True
            except Exception as e:
                print(f"can't clone repo: {e}")
                return False

    def _check_local_path(self, path: str) -> bool:
        # does path exist
        return os.path.isdir(path)

    def _check_repo_exists(self, path: str) -> bool:
        # does repo exist
        return self.repo.repo.exists(path)


class GitController:
    def __init__(self) -> None:
        self.git: Test_Git = self._get_git_instance()
        self.repo: Repo = None
        pass

    def git_ops_paths(self):
        # does path exist?  if not then create it
        if not self.git.test_check_local_path(path=self.git.args.git_path):
            # create path
            self.git.test_create_local_path()
        return

    def git_ops_init(self):
        self.git.test_init()

    def git_ops_remote_add(self):
        self.git.test_remote_add()

    def git_ops_test_create_index(self):
        self.git.test_create_index()

    def git_ops_add_files(self):
        self.git.test_files_add()

    def git_ops_commit(self):
        self.git.test_commit()

    def git_ops_remote_reference(self):
        self.git.test_set_remote_reference()

    def git_ops_push(self):
        self.git.test_push()

    def git_ops_pull(self):
        self.git.test_pull()

    # private
    def _get_git_instance(self):
        return Test_Git(args=Test_GitArgs())


def main():

    control = GitController()
    control.git_ops_paths()
    control.git_ops_init()
    control.git_ops_remote_add()
    control.git_ops_test_create_index()
    control.git_ops_add_files()
    control.git_ops_commit()
    control.git_ops_remote_reference()
    control.git_ops_push()
    control.git_ops_pull()


"""
class GitClone(Git):
    pass


class GitFetch(Git):
    pass


class GitPush(Git):
    pass
"""


if __name__ == "__main__":
    main()
