from io import BytesIO
from pathlib import Path
from typing import cast

from dulwich import patch
from dulwich import porcelain
from dulwich.diff_tree import tree_changes
from langchain.tools import tool
from langchain_core.tools import BaseTool, StructuredTool


class GitTools:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.repo = porcelain.open_repo(str(self.repo_path))

    def _get_branch_tree(self, branch_name: str) -> object:
        return self.repo[self.repo.refs[f'refs/heads/{branch_name}'.encode()]].tree

    def list_branches(self) -> list[str]:
        """List all branches in the local repository."""
        branches = []
        for ref in self.repo.refs.keys():
            if ref.startswith(b'refs/heads/'):
                branches.append(ref.decode().split('/')[-1])
        return sorted(branches)

    def diff_between_branches(self, branch1: str, branch2: str) -> str:
        """Get the diff between two branches."""
        tree1 = self._get_branch_tree(branch1)
        tree2 = self._get_branch_tree(branch2)

        changes = list(tree_changes(self.repo, tree1, tree2))

        result = []
        for change in changes:
            old_path = change.old.path.decode('utf-8') if change.old.path else None
            new_path = change.new.path.decode('utf-8') if change.new.path else None
            result.append(f"Type: {change.type}, Old: {old_path}, New: {new_path}")

        return "\n".join(result)

    def diff_file_content(self, branch1: str, branch2: str, file_path: str) -> str:
        """Get the diff of a file's content between two branches."""
        tree1 = self._get_branch_tree(branch1)
        tree2 = self._get_branch_tree(branch2)

        changes = list(tree_changes(self.repo, tree1, tree2))

        for change in changes:
            if change.type == 'modify' and change.new.path.decode('utf-8') == file_path:
                old_file = (change.old.path, change.old.mode, change.old.sha)
                new_file = (change.new.path, change.new.mode, change.new.sha)

                diff_output = BytesIO()
                patch.write_object_diff(diff_output, self.repo.object_store, old_file, new_file)
                return diff_output.getvalue().decode('utf-8')

        return f"No changes found for file {file_path}"

    def get_file_content(self, branch: str, file_path: str) -> str:
        """Get the full content of a file in a specific branch."""
        tree = self._get_branch_tree(branch)

        try:
            _, file_sha = self.repo[tree][file_path.encode()]
            return self.repo[file_sha].data.decode('utf-8')
        except KeyError:
            return f"File {file_path} not found in branch {branch}"

    def get_tools(self) -> list[BaseTool]:
        @tool
        def list_branches() -> list[str]:
            """List all branches in the local repository."""
            return self.list_branches()

        @tool
        def diff_between_branches(branch1: str, branch2: str) -> str:
            """Get the diff between two branches."""
            return self.diff_between_branches(branch1, branch2)

        @tool
        def diff_file_content(branch1: str, branch2: str, file_path: str) -> str:
            """Get the diff of a file's content between two branches."""
            return self.diff_file_content(branch1, branch2, file_path)

        @tool
        def get_file_content(branch: str, file_path: str) -> str:
            """Get the full content of a file in a specific branch."""
            return self.get_file_content(branch, file_path)

        return cast(list[BaseTool],
                    [list_branches, diff_between_branches, diff_file_content, get_file_content])

# Usage example:
# git_tools = GitTools('/path/to/local/repo')
# branches = git_tools.list_branches_int()
# diff = git_tools.diff_between_branches_int('main', 'dev')
# file_diff = git_tools.diff_file_content_int('main', 'dev', 'path/to/file.py')
# file_content = git_tools.get_file_content_int('main', 'path/to/file.py')
