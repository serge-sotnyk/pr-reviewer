from langchain.tools import tool
from dulwich.diff_tree import tree_changes
from dulwich import patch, porcelain
from io import BytesIO

from .git_repo_base import GitRepoBase


class GitTools(GitRepoBase):
    @tool
    def list_branches(self) -> str:
        """List all branches in the repository."""
        branches = porcelain.branch_list(self.repo)
        return "\n".join([branch.decode() for branch in branches])

    @tool
    def diff_between_branches(self, branch1: str, branch2: str) -> str:
        """Get the diff between two branches."""
        self.fetch_branch(branch1)
        self.fetch_branch(branch2)

        tree1 = self.get_branch_tree(branch1)
        tree2 = self.get_branch_tree(branch2)

        changes = list(tree_changes(self.repo, tree1, tree2))

        result = []
        for change in changes:
            old_path = change.old.path.decode('utf-8') if change.old.path else None
            new_path = change.new.path.decode('utf-8') if change.new.path else None
            result.append(f"Type: {change.type}, Old: {old_path}, New: {new_path}")

        return "\n".join(result)

    @tool
    def diff_file_content(self, branch1: str, branch2: str, file_path: str) -> str:
        """Get the diff of a file's content between two branches."""
        self.fetch_branch(branch1)
        self.fetch_branch(branch2)

        tree1 = self.get_branch_tree(branch1)
        tree2 = self.get_branch_tree(branch2)

        changes = list(tree_changes(self.repo, tree1, tree2))

        for change in changes:
            if change.type == 'modify' and change.new.path.decode('utf-8') == file_path:
                old_file = (change.old.path, change.old.mode, change.old.sha)
                new_file = (change.new.path, change.new.mode, change.new.sha)

                diff_output = BytesIO()
                patch.write_object_diff(diff_output, self.repo.object_store, old_file, new_file)
                return diff_output.getvalue().decode('utf-8')

        return f"No changes found for file {file_path}"

    @tool
    def get_file_content(self, branch: str, file_path: str) -> str:
        """Get the full content of a file in a specific branch."""
        self.fetch_branch(branch)

        tree = self.get_branch_tree(branch)

        try:
            file_sha = tree[file_path.encode()]
            return self.repo[file_sha].data.decode('utf-8')
        except KeyError:
            return f"File {file_path} not found in branch {branch}"

# Usage example:
# with GitTools('https://github.com/example/repo.git') as git_tools:
#     branches = git_tools.list_branches()
#     diff = git_tools.diff_between_branches('main', 'dev')
#     file_diff = git_tools.diff_file_content('main', 'dev', 'path/to/file.py')
#     file_content = git_tools.get_file_content('main', 'path/to/file.py')
