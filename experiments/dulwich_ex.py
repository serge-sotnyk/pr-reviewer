from io import BytesIO
from pathlib import Path

from dulwich import porcelain, patch
from dulwich.diff_tree import tree_changes
from dulwich.repo import Repo

root = Path(__file__).parent.parent
repo = Repo(str(root))

# Fetch the latest changes from the remote repository
porcelain.fetch(repo, 'origin')

# Ensure the local 'dev' branch exists and is up-to-date with 'origin/dev'
if b'refs/remotes/origin/dev' in repo.refs:
    repo[b'refs/heads/dev'] = repo.refs[b'refs/remotes/origin/dev']

# Get the commits for the branches
main_commit = repo[b'refs/heads/main'].id
dev_commit = repo[b'refs/heads/dev'].id

# Get the trees for each commit
main_tree = repo[main_commit].tree
dev_tree = repo[dev_commit].tree

# Get the diff between the trees
changes = list(tree_changes(repo, main_tree, dev_tree))

# Process and display the changes
for change in changes:
    old_path = change.old.path
    old_path_str = old_path.decode('utf-8') if old_path else None
    new_path = change.new.path
    new_path_str = new_path.decode('utf-8') if new_path else None
    print(f"Change type: {change.type}")
    print(f"Old path: {old_path_str}")
    print(f"New path: {new_path_str}")

    if change.type == 'modify':
        old_file = (old_path, change.old.mode, change.old.sha)
        new_file = (new_path, change.new.mode, change.new.sha)

        # Generate the diff between the two blobs
        diff_output = BytesIO()
        patch.write_object_diff(diff_output, repo.object_store, old_file, new_file)
        print(diff_output.getvalue().decode('utf-8'))
    print("-" * 40)
