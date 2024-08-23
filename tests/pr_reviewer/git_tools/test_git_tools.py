from pathlib import Path

from pr_reviewer.git_tools.git_tools import GitTools

REPO_URL = "git@github.com:serge-sotnyk/pr-reviewer-test.git"
REPO_NAME = REPO_URL.split('/')[-1].replace('.git', '')


def find_test_repo_path():
    """Find the path to the repository by traversing upwards from the current source directory."""
    repo_path = Path(__file__).parent
    while True:
        if (repo_path / REPO_NAME).is_dir():
            return repo_path / REPO_NAME
        if repo_path == repo_path.parent:
            raise FileNotFoundError(f"Could not find {REPO_NAME} in the path. Please, run "
                                    f"prepare_test_repo.py script.")
        repo_path = repo_path.parent


test_repo_path = find_test_repo_path()


def test_list_branches():
    git_tools = GitTools(test_repo_path)
    branches = git_tools.list_branches_int()
    assert len(branches) > 0
    assert "main" in branches


def test_diff_between_branches():
    git_tools = GitTools(test_repo_path)
    diff = git_tools.diff_between_branches_int("main", "test")
    assert diff


def test_diff_file_content_int():
    git_tools = GitTools(test_repo_path)
    diff = git_tools.diff_file_content_int("main", "test", "file_to_modify.txt")
    assert diff


def test_get_file_content():
    git_tools = GitTools(test_repo_path)
    content_main = git_tools.get_file_content_int("main", "file_to_modify.txt")
    assert "Row to deletion" in content_main
    assert "Row to change" in content_main
    assert "Row changed" not in content_main
    assert "And added row" not in content_main

    content_test = git_tools.get_file_content_int("test", "file_to_modify.txt")
    assert "Row to deletion" not in content_test
    assert "Row to change" not in content_test
    assert "Row changed" in content_test
    assert "And added row" in content_test
