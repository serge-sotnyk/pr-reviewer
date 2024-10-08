from io import BytesIO
from pathlib import Path
from typing import cast, Annotated

from dulwich import patch
from dulwich import porcelain
from dulwich.diff_tree import tree_changes
from langchain.tools import tool
from langchain_core.tools import BaseTool


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

    def _get_tree_changes(self, base_branch: str, feature_branch: str) -> list:
        base_tree = self._get_branch_tree(base_branch)
        feature_tree = self._get_branch_tree(feature_branch)
        return list(tree_changes(self.repo, base_tree, feature_tree))

    def diff_between_branches(self, base_branch: str, feature_branch: str) -> str:
        """Get the diff between two branches."""
        changes = self._get_tree_changes(base_branch, feature_branch)

        result = []
        for change in changes:
            old_path = change.old.path.decode('utf-8') if change.old.path else None
            new_path = change.new.path.decode('utf-8') if change.new.path else None
            result.append(f"Type: {change.type}, Old: {old_path}, New: {new_path}")

        return "\n".join(result) if result \
            else f"Branches `{base_branch}` and `{feature_branch}` have the same content"

    def diff_file_content(self, base_branch: str, feature_branch: str, file_path: str) -> str:
        """Get the diff of a file's content between two branches."""
        changes = self._get_tree_changes(base_branch, feature_branch)

        for change in changes:
            if change.new.path and (change.new.path.decode('utf-8') != file_path):
                continue
            if change.type == 'modify':
                old_file = (change.old.path, change.old.mode, change.old.sha)
                new_file = (change.new.path, change.new.mode, change.new.sha)

                diff_output = BytesIO()
                patch.write_object_diff(diff_output, self.repo.object_store, old_file, new_file)
                return diff_output.getvalue().decode('utf-8')
            if change.type == 'add':
                content = self.get_file_content(feature_branch, file_path)
                content = [f"+{line}" for line in content.splitlines()]
                return "\n".join(content)
            if change.type == 'delete':
                content = self.get_file_content(base_branch, file_path)
                content = [f"-{line}" for line in content.splitlines()]
                return "\n".join(content)

        return f"No changes found for file {file_path}"

    def get_file_content(self, branch: str, file_path: str) -> str:
        """Get the full content of a file in a specific branch, including files in
        subdirectories."""
        tree = self._get_branch_tree(branch)

        # Split the file path into parts and filename
        *path_parts, fn = file_path.split('/')

        # Traverse the tree structure
        current_tree = tree
        for part in path_parts:
            try:
                mode, sha = self.repo[current_tree][part.encode()]
                if mode & 0o040000:  # Directory
                    current_tree = sha  # Just store the SHA, not the Tree object
                else:
                    return f"Path {'/'.join(path_parts)} is not a directory in branch {branch}"
            except KeyError:
                return f"Directory {part} not found in path {file_path} in branch {branch}"

        # Get the file content
        try:
            mode, file_sha = self.repo[current_tree][fn.encode()]
            return self.repo[file_sha].data.decode('utf-8')
        except KeyError:
            return f"File {file_path} not found in branch {branch}"

    def get_tools(self) -> list[BaseTool]:
        @tool
        def list_branches() -> list[str]:
            """List all branches in the local repository."""
            return self.list_branches()

        @tool
        def diff_between_branches(
                base_branch: Annotated[str, "The branch with the original code"],
                feature_branch: Annotated[str, "The branch with the modified code"],
        ) -> str:
            """Get the diff between two branches."""
            return self.diff_between_branches(base_branch, feature_branch)

        @tool
        def diff_file_content(
                base_branch: Annotated[str, "The branch with the original code"],
                feature_branch: Annotated[str, "The branch with the modified code"],
                file_path: Annotated[str, "The path to the file in the repository"],
        ) -> str:
            """Get the diff of a file's content between two branches."""
            return self.diff_file_content(base_branch, feature_branch, file_path)

        @tool
        def get_file_content(
                branch: Annotated[str, "The branch to get the file content from"],
                file_path: Annotated[str, "The path to the file in the repository"],
        ) -> str:
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
