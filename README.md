# pr-reviewer
Test task for NameCheap

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

## Additional Notes

- Ensure that the local directory you're mounting has the necessary permissions for the container to read and write.
- The working directory inside the container is set to `/work`, so all paths should be relative to this.
- If you need to run multiple commands or use a shell inside the container, you can use:

  Linux/macOS:
  ```bash
  docker run --rm -it --env-file .env -v /path/to/local/repo:/work/repo atepeq/pr-reviewer:latest /bin/bash
  ```

  Windows (Command Prompt):
  ```cmd
  docker run --rm -it --env-file .env -v C:\path\to\local\repo:/work/repo atepeq/pr-reviewer:latest /bin/bash
  ```

  This will give you a shell inside the container where you can run the Python scripts directly.

- On Windows, you may need to enable file sharing for the drive you're mounting. You can do this in Docker Desktop settings under "Resources" > "File Sharing".
- When using Command Prompt on Windows, the caret (^) is used for line continuation instead of the backslash (\) used in bash.
- Windows paths use backslashes (\) by default, but Docker requires forward slashes (/) for volume mounting. Make sure to use forward slashes when specifying the path in the Docker command.
- In Windows Command Prompt, environment variables are referenced using %VARIABLE% syntax instead of $VARIABLE.