import os
from dataclasses import dataclass
from abc import ABC, abstractmethod

# from git import Repo


@dataclass
class GitArgs:

    git_path: str = "/tmp/git/backups"
    git_server: str = "gitea.wizznet.co.uk"
    git_repo_name: str = "backuprepo"
    command_type: tuple = ("CLONE", "FETCH", "COMMIT", "PUSH")


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
    def __init__(self, git_args: GitArgs) -> None:
        super().__init__()

        self.git_args = git_args

    pass

    def clone():
        pass

    def commit():
        pass

    def fetch():
        pass

    def push():
        pass

    # create path
    def create_local_path(self):
        # Create path
        from pathlib import Path

        return Path(self.test_git_args.git_path).mkdir(parents=True, exist_ok=True)

    # @pytest.mark.parametrize
    def check_local_path(self, path):
        # does path exist
        return os.path.isdir(path)


"""
class GitClone(Git):
    pass


class GitFetch(Git):
    pass


class GitPush(Git):
    pass
"""
