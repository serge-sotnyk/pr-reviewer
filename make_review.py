import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from pr_reviewer.git_tools.git_tools import GitTools
from pr_reviewer.simple_reviewer import make_review

load_dotenv()


def initialize_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Review changes between two branches in a repository.")
    parser.add_argument("-p", "--path", type=Path, required=True,
                        help="Path to the local repository")
    parser.add_argument("-s", "--source_branch", help="Name of the new branch")
    parser.add_argument("-d", "--destination_branch",
                        help="Name of the destination branch")
    parser.add_argument("-r", "--result",
                        help="Filename for storing execution result")
    parser.add_argument(
        "-m", "--model", default="llama-3.1-70b-versatile",
        help="Name of the model to use (e.g., gpt-4o-mini, llama-3.1-70b-versatile). "
             "If model name starting with 'gpt' will use OpenAI provider, otherwise Groq provider."
    )
    return parser.parse_args()


def validate_repository(path: Path):
    if not path.is_dir():
        print(f"Error: The specified path '{path}' is not a valid directory.")
        sys.exit(1)


def determine_branches(git_tools: GitTools, args: argparse.Namespace) -> tuple[str, str]:
    local_branches = git_tools.list_branches()

    source_branch = args.source_branch or next(
        (branch for branch in local_branches if branch not in {'main', 'master'}), None)
    if not source_branch:
        print(
            "Error: Could not determine source branch. "
            "Please specify it using -s/--source_branch.")
        sys.exit(1)

    destination_branch = args.destination_branch or next(
        (branch for branch in local_branches if branch in {'main', 'master'}), None)
    if not destination_branch:
        print(
            "Error: Could not determine destination branch. "
            "Please specify it using -d/--destination_branch.")
        sys.exit(1)

    return source_branch, destination_branch


def store_results(review: str, result_file: str = ''):
    if result_file:
        with open(result_file, 'wt', encoding='utf-8') as f:
            f.write(review)
        print(f"Review has been written to {result_file}")
    else:
        print("Review:")
        print(review)


def main():
    args = initialize_arguments()
    validate_repository(args.path)

    git_tools = GitTools(str(args.path))
    source_branch, destination_branch = determine_branches(git_tools, args)

    review = make_review(args.path, destination_branch, source_branch, args.model)
    store_results(review, args.result)


if __name__ == "__main__":
    main()
