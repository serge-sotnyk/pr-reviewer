# pr-reviewer
Test task for NameCheap
* https://youtu.be/dudpBnMJR80 - Video with comments about this test-task (in Ukrainian)

# Current agent limitations:
At present, I've used the simplest single agent. The prompt isn't very complex. By 
default, it uses a model that isn't the best (but one that Groq allows to try for 
free). Nevertheless, we can see a somewhat plausible output.

I'm confident that the agent can be easily and significantly improved by trying the 
following changes:

* Use a better model (gpt4-omni / claude-3.5-sonnet)
* Create a team of agents, each specializing in their own area (this usually improves 
  the quality of responses)
* Create a database of guidelines for code review
* Work on prompts (for example, try different approaches like ReAct, CoT, etc., or 
  evolutionary approaches, although this is not as straightforward)

However, all of this is pointless until we have a way to measure quality. In other 
words, we need metrics and a dataset on which we would measure this. I don't think 
I'll create it very quickly for this task, although LLMs will help us with this as 
well. I would start with the following approach:

1. Take a code base. (How much? Which languages?)
2. Using a good model (for example, claude-3.5-sonnet - it works best with code for 
  me so far), create commits where there are some code flaws. This is a separate task 
  that needs to be well-thought-out and properly prompted. Yes, this is synthetic, but 
  I'm sure it will allow us to measure how well the reviewer works.
3. The reviewer should also be evaluated by an LLM. I think a cheaper one will do here 
  (this is important because metrics will be run quite often), as it will only need to 
  understand whether the reviewer described the flaw that the large and high-quality 
  model introduced. This is a simpler task.
4. If it's possible to add real data somehow (for example, if there's a database of 
  pull requests and reviews from humans), that would be good too.

Only after setting up the metric calculation can we start improving anything.

There's also an untapped field in testing on various cases:
* Regular cases
* Various edge cases
* Large volumes of code

We can also add various tools for working with the repository - I've only implemented 
the minimal toolbox.

# Repository Utilities

This repository contains two utilities for managing and reviewing Git repositories:

1. `prepare_repo.py`: Downloads and prepares a Git repository for review.
2. `make_review.py`: Performs a code review on changes between branches.

## Installation

This project uses Poetry for dependency management. Follow these steps to set up 
your environment:

### Method 1: Standard Installation

1. Ensure you have Python 3.11 or newer and Poetry installed on your system.
2. Clone this repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```
3. Install dependencies using Poetry:
   ```
   poetry install
   ```
4. Activate the virtual environment:
   ```
   poetry shell
   ```

### Method 2: Alternative Installation for Windows

This method can be used on Windows systems without installed globally Poetry.

1. Create a virtual environment with Python 3.11:
   ```
   python3.11 -m venv venv
   ```
2. Activate the virtual environment:
   ```
   venv\Scripts\activate
   ```
3. Install Poetry within the virtual environment:
   ```
   pip install poetry
   ```
4. Use Poetry to install project dependencies:
   ```
   poetry install
   ```

Choose the method that works best for your setup and preferences.

### Environment Variables
Please copy the `.env-example` file to `.env` and fill in the required 
environment variables.

## Usage

### prepare_repo.py

This utility downloads a specified Git repository and prepares it for review.
This version targeted on public repositories. If you want to test agents on private
repositories, please clone them manually.

```
python prepare_repo.py [-h] -r REPO [-p PATH] [branches ...]
```

Parameters:
- `-r, --repo REPO`: URL of the Git repository (required)
- `-p, --path PATH`: Local path for the repository
- `branches`: List of branches to download (optional, leave empty for all branches)

Examples:
```
# List remote branches
python prepare_repo.py -r https://github.com/user/repo

# Clone repository with all branches
python prepare_repo.py -r https://github.com/user/repo -p ./local_repo

# Clone repository with specific branches
python prepare_repo.py -r https://github.com/user/repo -p ./local_repo main develop
```

### make_review.py

This utility performs a code review on changes between two branches in a repository.
We assume that these branches are the part of the pull request.

```
python make_review.py [-h] -p PATH [-s SOURCE_BRANCH] [-d DESTINATION_BRANCH] [-r RESULT] [-m MODEL]
```

Parameters:
- `-p, --path PATH`: Path to the local repository (required)
- `-s, --source_branch`: Name of the new branch (optional). If not provided, the first branch with name 
  not equal to `main` or `master` will be used.
- `-d, --destination_branch`: Name of the destination branch (optional). If not provided, the `main` 
  or `master` branch will be used.
- `-r, --result`: Filename for storing execution result (optional). If not provided, the result will 
  be printed in the console.
- `-m, --model`: Name of the model to use (default: "llama-3.1-70b-versatile"). Right now,
  we support models from OpenAI and Groq. If the model name starts with 'gpt', it will use the OpenAI provider;
  otherwise, it will use the Groq provider. Please, check if you fill the proper API key in the `.env` file.

Examples:
```
# Review changes between auto-detected branches
python make_review.py -p ./local_repo

# Review changes with specified branches and output file
python make_review.py -p ./local_repo -s feature-branch -d main -r review_output.txt

# Review changes using a specific model
python make_review.py -p ./local_repo -m gpt-4-mini
```

Note: If the model name starts with 'gpt', it will use the OpenAI provider; otherwise, it will use the Groq provider.

## Workflow

1. Use `prepare_repo.py` to download and set up the repository you want to review.
2. Use `make_review.py` to perform a code review on the changes between branches in the prepared repository.

Remember to activate the virtual environment before running these scripts.


# PR Reviewer Docker Image Usage Instructions

Image name: `atepeq/pr-reviewer:latest`

## 1. Building the Docker Image

To build the Docker image, follow these steps:

1. Navigate to the directory containing the Dockerfile.
2. Retrieve the version from the VERSION file:
   
   Linux/macOS:
   ```bash
   VERSION=$(cat VERSION)
   ```
   
   Windows (Command Prompt):
   ```cmd
   set /p VERSION=<VERSION
   ```

3. Build the image with both 'latest' and version tags:
   
   Linux/macOS:
   ```bash
   docker build -t atepeq/pr-reviewer:latest -t atepeq/pr-reviewer:$VERSION .
   ```
   
   Windows (Command Prompt):
   ```cmd
   docker build -t atepeq/pr-reviewer:latest -t atepeq/pr-reviewer:%VERSION% .
   ```

## 2. Pushing to Docker Hub

After building the image, push it to Docker Hub:

Linux/macOS:
```bash
docker push atepeq/pr-reviewer:latest
docker push atepeq/pr-reviewer:$VERSION
```

Windows (Command Prompt):
```cmd
docker push atepeq/pr-reviewer:latest
docker push atepeq/pr-reviewer:%VERSION%
```

Note: Ensure you're logged in to Docker Hub (`docker login`) before pushing.

## 3. Downloading the Image

To download the image from Docker Hub:

Linux/macOS/Windows:
```bash
docker pull atepeq/pr-reviewer:latest
```

Or for a specific version:

Linux/macOS:
```bash
docker pull atepeq/pr-reviewer:$VERSION
```

Windows (Command Prompt):
```cmd
docker pull atepeq/pr-reviewer:%VERSION%
```

## 4. Running the Image

To run the image with a local folder attached and environment variables from a .env file:

### Prepare the Environment

1. Create a `.env` file in your local directory with the necessary environment variables.
2. Prepare a local directory to mount in the container (e.g., `/path/to/local/repo` on Linux/macOS or `C:\path\to\local\repo` on Windows).

### Running prepare_repo.py

Linux/macOS:
```bash
docker run --rm -it \
  --env-file .env \
  -v /path/to/local/repo:/work/repo \
  atepeq/pr-reviewer:latest \
  python prepare_repo.py -r <REPO_URL> -p /work/repo [BRANCHES...]
```

Windows (Command Prompt):
```cmd
docker run --rm -it ^
  --env-file .env ^
  -v C:\path\to\local\repo:/work/repo ^
  atepeq/pr-reviewer:latest ^
  python prepare_repo.py -r <REPO_URL> -p /work/repo [BRANCHES...]
```

Replace `<REPO_URL>` with the actual repository URL and `[BRANCHES...]` with the branches you want to prepare (optional).

### Running make_review.py

Linux/macOS:
```bash
docker run --rm -it \
  --env-file .env \
  -v /path/to/local/repo:/work/repo \
  atepeq/pr-reviewer:latest \
  python make_review.py -p /work/repo -s <SOURCE_BRANCH> -d <DESTINATION_BRANCH> [-r <RESULT_FILE>]
```

Windows (Command Prompt):
```cmd
docker run --rm -it ^
  --env-file .env ^
  -v C:\path\to\local\repo:/work/repo ^
  atepeq/pr-reviewer:latest ^
  python make_review.py -p /work/repo -s <SOURCE_BRANCH> -d <DESTINATION_BRANCH> [-r <RESULT_FILE>]
```

Replace `<SOURCE_BRANCH>`, `<DESTINATION_BRANCH>`, and optionally `<RESULT_FILE>` with appropriate values.

Note: If you specify a `<RESULT_FILE>`, make sure it's within the mounted directory to access it from your host machine.
