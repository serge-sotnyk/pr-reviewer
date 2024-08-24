import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from pr_reviewer.git_tools.git_tools import GitTools
from pr_reviewer.simple_reviewer import make_review

load_dotenv()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Review changes between two branches in a repository.")
    parser.add_argument("-p", "--path", type=Path, required=True,
                        help="Path to the local repository")
    parser.add_argument("-s", "--source_branch", help="Name of the new branch")
    parser.add_argument("-d", "--destination_branch",
                        help="Name of the destination branch")
    parser.add_argument("-r", "--result",
                        help="Filename for storing execution result")

    args = parser.parse_args()

    # Validate repository path
    if not args.path.is_dir():
        print(f"Error: The specified path '{args.path}' is not a valid directory.")
        sys.exit(1)

    # Initialize GitTools
    git_tools = GitTools(str(args.path))

    # Get local branches
    local_branches = git_tools.list_branches()

    # Determine source branch
    if not args.source_branch:
        args.source_branch = next(
            (branch for branch in local_branches if branch not in {'main', 'master'}), None)
        if not args.source_branch:
            print(
                "Error: Could not determine source branch. "
                "Please specify it using -s/--source_branch.")
            sys.exit(1)

    # Determine destination branch
    if not args.destination_branch:
        args.destination_branch = next(
            (branch for branch in local_branches if branch in {'main', 'master'}), None)
        if not args.destination_branch:
            print(
                "Error: Could not determine destination branch. "
                "Please specify it using -d/--destination_branch.")
            sys.exit(1)

    # Make the review
    review = make_review(args.path, args.destination_branch, args.source_branch)

    # Output the result
    if args.result:
        open(args.result, 'wt', encoding='utf-8').write(review)
        print(f"Review has been written to {args.result}")
    else:
        print("Review:")
        print(review)
