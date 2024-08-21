from dulwich.repo import Repo
from dulwich.diff_tree import tree_changes
from dulwich import porcelain

# Clone the repository
# repo = porcelain.clone('https://github.com/user/repo.git', '/path/to/local/repo')

# Open the repository
repo = Repo('/path/to/local/repo')

# Get the commits for the branches
master_commit = repo[b'refs/heads/master'].id
feature_commit = repo[b'refs/heads/feature_branch'].id

# Get the trees (file states) for each commit
master_tree = repo[master_commit].tree
feature_tree = repo[feature_commit].tree

# Get the diff between the trees
changes = list(tree_changes(repo, master_tree, feature_tree))

# Print the changes
for change in changes:
    print(change)