import os
from pathlib import Path

from dulwich import porcelain


class GitRepoBase:
    def __init__(self, repo_url: str):
        self.repo_url = repo_url
        self.temp_dir = Path(os.environ.get('GIT_TEMP_ROOT', '/tmp')) / 'git_repo'
        self.repo = None

    def __enter__(self) -> 'GitRepoBase':
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.repo = porcelain.clone(self.repo_url, str(self.temp_dir))
        return self

    def __exit__(self, exc_type: type, exc_val: Exception, exc_tb: object):
        if self.repo:
            self.repo.close()

    def fetch_branch(self, branch_name: str):
        porcelain.fetch(self.repo, 'origin')
        if f'refs/remotes/origin/{branch_name}'.encode() in self.repo.refs:
            self.repo[f'refs/heads/{branch_name}'.encode()] = self.repo.refs[
                f'refs/remotes/origin/{branch_name}'.encode()]

    def get_branch_commit(self, branch_name: str) -> bytes:
        return self.repo[f'refs/heads/{branch_name}'.encode()].id

    def get_branch_tree(self, branch_name: str) -> object:
        commit = self.get_branch_commit(branch_name)
        return self.repo[commit].tree
