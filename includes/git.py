from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class GitArgs:

    git_folder: str

    command_type: tuple = ("CLONE", "FETCH")


class BaseGit(ABC):
    pass


class GitClone(BaseGit):
    pass


class GitFetch(BaseGit):
    pass


class GitPush(BaseGit):
    pass
