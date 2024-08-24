import argparse
from pathlib import Path

from dulwich import porcelain
from dulwich.client import get_transport_and_path
from dulwich.repo import Repo


def list_remote_branches(repo_url: str) -> list[str]:
    client, remote_path = get_transport_and_path(repo_url)
    remote_refs = client.get_refs(remote_path)
    branches = [ref.decode("utf-8").split("/")[-1] for ref in remote_refs if
                ref.startswith(b"refs/heads/")]
    return branches


def sync_repo(repo_path: Path, repo_url: str, branches: list[str]):
    print(f"Repository already exists. Synchronizing...")
    repo = Repo(str(repo_path))

    client, remote_path = get_transport_and_path(repo_url)
    fetch_result = client.fetch(remote_path, repo)

    print("Fetched changes from remote.")

    for remote_ref, sha in fetch_result.refs.items():
        if remote_ref.startswith(b'refs/heads/'):
            branch_name = remote_ref.decode('utf-8').split('/')[-1]
            if not branches or branch_name in branches:
                print(f"Updating branch: {branch_name}")
                repo.refs[f'refs/heads/{branch_name}'.encode()] = sha
                repo.refs[f'refs/remotes/origin/{branch_name}'.encode()] = sha

    print("Synchronization completed.")


def clone_repo(repo_path: Path, repo_url: str, branches: list[str]):
    print(f"Cloning repository...")
    porcelain.clone(repo_url, str(repo_path), depth=1)

    repo = Repo(str(repo_path))
    client, remote_path = get_transport_and_path(repo_url)
    remote_refs = client.get_refs(remote_path)

    for ref_name, sha in remote_refs.items():
        if ref_name.startswith(b"refs/heads/"):
            branch_name = ref_name.decode("utf-8").split("/")[-1]
            if not branches or branch_name in branches:
                print(f"Creating local branch: {branch_name}")
                repo.refs[f'refs/heads/{branch_name}'.encode()] = sha
                repo.refs[f'refs/remotes/origin/{branch_name}'.encode()] = sha

    print("Cloning and branch setup completed.")


def main():
    parser = argparse.ArgumentParser(
        description="Prepare a Git repository with specific branches.")
    parser.add_argument("-r", "--repo", required=True,
                        help="URL of the Git repository")
    parser.add_argument("-p", "--path", help="Local path for the repository")
    parser.add_argument("branches", nargs="*",
                        help="List of branches to download (empty for all branches)")

    args = parser.parse_args()

    if not args.path:
        remote_branches = list_remote_branches(args.repo)
        print("Remote branches:")
        for branch in remote_branches:
            print(f"- {branch}")
        return

    repo_path = Path(args.path)

    if repo_path.exists():
        sync_repo(repo_path, args.repo, args.branches)
    else:
        clone_repo(repo_path, args.repo, args.branches)


if __name__ == "__main__":
    main()
