from pr_reviewer.git_tools.git_tools import GitTools

test_repo_url = "git@github.com:serge-sotnyk/pr-reviewer-test.git"


def test_list_branches():
    with GitTools(test_repo_url) as git_tools:
        branches = git_tools.list_branches_int()
        assert len(branches) > 0
        assert "main" in branches
