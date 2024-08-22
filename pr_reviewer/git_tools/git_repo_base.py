import os
import re
import shutil
import time
import warnings
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from dulwich import porcelain


def sanitize_repo_name(repo_url: str, max_length: int = 60) -> str:
    parsed_url = urlparse(repo_url)

    # If it's an SSH URL, convert it to a path-like format
    if '@' in parsed_url.path:
        path = parsed_url.path.split(':', 1)[-1]
    else:
        path = parsed_url.path.lstrip('/')

    # Remove .git extension if present
    path = path.rstrip('.git')

    # Replace non-alphanumeric characters with underscores
    sanitized = re.sub(r'[^\w.-]', '_', path)

    # Truncate to max_length, ensuring we don't cut in the middle of a word
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rsplit('_', 1)[0]

    return sanitized.encode('ascii', 'ignore').decode('ascii')


class GitRepoBase:
    def __init__(self, repo_url: str, cleanup_older_than: int = 3600):
        self.repo_url = repo_url
        self.base_dir = Path(os.environ.get('GIT_TEMP_ROOT', '/tmp')) / 'git_repo'
        self.repo_name = sanitize_repo_name(repo_url)
        self.temp_dir: Path|None = None
        self.repo = None
        if cleanup_older_than>0:
            self._cleanup_old_dirs(cleanup_older_than)

    def __enter__(self) -> 'GitRepoBase':
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._create_temp_dir()
        self.repo = porcelain.clone(self.repo_url, str(self.temp_dir))
        return self

    def __exit__(self, exc_type: type, exc_val: Exception, exc_tb: object):
        if self.repo:
            self.repo.close()

    def _cleanup_old_dirs(self, cleanup_older_than):
        assert cleanup_older_than > 0
        current_time = time.time()
        for dir_path in self.base_dir.glob('*'):
            if dir_path.is_dir():
                dir_age = current_time - dir_path.stat().st_mtime
                if dir_age > cleanup_older_than:
                    try:
                        shutil.rmtree(dir_path)
                    except (PermissionError, FileNotFoundError, OSError) as e:
                        warnings.warn(
                            f"Failed to remove old directory {dir_path}: {type(e).__name__}: {e}")

    def _create_temp_dir(self):
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        dir_name = f"{timestamp}_{self.repo_name}"
        self.temp_dir = self.base_dir / dir_name
        self.temp_dir.mkdir(parents=True, exist_ok=True)

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
