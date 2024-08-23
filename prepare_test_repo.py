from pathlib import Path
from dulwich import porcelain
from dulwich.repo import Repo

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

    # Get all remote branches
    remote_refs = porcelain.ls_remote(REPO_URL)

    for ref_name, _ in remote_refs.items():
        if ref_name.startswith(b"refs/heads/"):
            branch_name = ref_name.decode("utf-8").split("/")[-1]
            print(f"Synchronizing branch: {branch_name}")

            # Fetch changes for each branch
            porcelain.fetch(repo, REPO_URL)

            # Update the local branch
            remote_branch = repo[f'refs/remotes/origin/{branch_name}'.encode()]
            repo[f'refs/heads/{branch_name}'.encode()] = remote_branch.id

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
