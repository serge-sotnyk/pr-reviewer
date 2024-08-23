from pathlib import Path
from dulwich import porcelain
from dulwich.repo import Repo
from dulwich.client import get_transport_and_path

# Constants
REPO_URL = "git@github.com:serge-sotnyk/pr-reviewer-test.git"
REPO_NAME = REPO_URL.split('/')[-1].replace('.git', '')


def get_repo_path() -> Path:
    """Determine the path for the repository."""
    root_dir = Path(__file__).parent.parent
    return root_dir / REPO_NAME


def sync_repo(repo_path: Path):
    """Synchronize existing repository."""
    print(f"Repository {REPO_NAME} already exists. Synchronizing...")
    repo = Repo(str(repo_path))

    # Fetch all changes from remote
    client, remote_path = get_transport_and_path(REPO_URL)
    fetch_result = client.fetch(remote_path, repo)

    print("Fetched changes from remote.")

    # Update all local branches
    for remote_ref, sha in fetch_result.refs.items():
        if remote_ref.startswith(b'refs/heads/'):
            branch_name = remote_ref.decode('utf-8').split('/')[-1]
            print(f"Updating branch: {branch_name}")

            # Update or create the local branch
            repo.refs[f'refs/heads/{branch_name}'.encode()] = sha

            # Update the remote tracking branch
            repo.refs[f'refs/remotes/origin/{branch_name}'.encode()] = sha

    # Remove local branches that no longer exist on remote
    remote_branches = [ref.decode('utf-8').split('/')[-1] for ref in fetch_result.refs if
                       ref.startswith(b'refs/heads/')]
    local_branches = [ref.split(b'/')[-1].decode('utf-8') for ref in repo.refs.keys() if
                      ref.startswith(b'refs/heads/')]

    for branch_name in local_branches:
        if branch_name not in remote_branches:
            print(f"Removing obsolete local branch: {branch_name}")
            del repo.refs[f'refs/heads/{branch_name}'.encode()]

    print("Synchronization completed.")


def clone_repo(repo_path: Path):
    """Clone repository and set up branches."""
    print(f"Repository {REPO_NAME} not found. Cloning...")
    porcelain.clone(REPO_URL, str(repo_path), depth=1)

    repo = Repo(str(repo_path))

    # Get all remote branches after cloning
    remote_refs = porcelain.ls_remote(REPO_URL)

    for ref_name, _ in remote_refs.items():
        if ref_name.startswith(b"refs/heads/") and ref_name != b"refs/heads/main":
            branch_name = ref_name.decode("utf-8").split("/")[-1]
            print(f"Creating local branch: {branch_name}")

            # Create a local branch for each remote branch
            porcelain.update_head(repo, ref_name)

    print("Cloning completed.")


def main():
    repo_path = get_repo_path()

    if repo_path.exists():
        sync_repo(repo_path)
    else:
        clone_repo(repo_path)


if __name__ == "__main__":
    main()
