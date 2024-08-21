from pathlib import Path

from dulwich.repo import Repo
from dulwich.diff_tree import tree_changes
from dulwich import porcelain

root = Path(__file__).parent.parent

# Clone the repository
# repo = porcelain.clone('https://github.com/user/repo.git', '/path/to/local/repo')

# Open the repository
repo = Repo(str(root))

# Fetch the latest changes from the remote repository
porcelain.fetch(repo, 'origin')
# Check if the branch exists, otherwise create it
if b'refs/remotes/origin/test' in repo.refs:
    # Create a local tracking branch if it doesn't exist
    repo[b'refs/heads/test'] = repo.refs[b'refs/remotes/origin/test']

# Get the commits for the branches
master_commit = repo[b'refs/heads/main'].id
feature_commit = repo[b'refs/heads/test'].id

# Get the trees (file states) for each commit
master_tree = repo[master_commit].tree
feature_tree = repo[feature_commit].tree

# Get the diff between the trees
changes = list(tree_changes(repo, master_tree, feature_tree))

# Print the changes
for change in changes:
    print(change)
