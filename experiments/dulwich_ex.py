from pathlib import Path
from dulwich.repo import Repo
from dulwich.diff_tree import tree_changes
from dulwich import porcelain, patch

root = Path(__file__).parent.parent

# Open the local repository
repo = Repo(str(root))

# Fetch the latest changes from the remote repository
porcelain.fetch(repo, 'origin')

# Create the local branch if it doesn't exist
if b'refs/remotes/origin/dev' in repo.refs:
    repo[b'refs/heads/dev'] = repo.refs[b'refs/remotes/origin/dev']

# Get the commits for the branches
master_commit = repo[b'refs/heads/main'].id
feature_commit = repo[b'refs/heads/dev'].id

# Get the trees for each commit
master_tree = repo[master_commit].tree
feature_tree = repo[feature_commit].tree

# Get the diff between the trees
changes = list(tree_changes(repo, master_tree, feature_tree))

# Process and display the changes
for change in changes:
    if change.type == 'modify':
        # Get the contents of the old and new versions of the file
        old_blob = repo.get_blob(change.old.sha)
        new_blob = repo.get_blob(change.new.sha)

        # Generate a patch (diff) between the two versions of the file
        diff = patch.diff_tree(repo.object_store, old_blob, new_blob)

        # Print the diff
        print(f"Changes in file: {change.old.path.decode('utf-8')}")
        for line in diff:
            print(line.decode('utf-8'))
    else:
        # For other change types (e.g., delete, add), just display the change details
        print(f"Change type: {change.type}")
        print(f"Old: {change.old}")
        print(f"New: {change.new}")
        print("-" * 40)
