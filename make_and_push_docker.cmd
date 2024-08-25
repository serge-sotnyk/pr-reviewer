@echo off
REM Read the version from the VERSION file
set /p VERSION=<VERSION

REM Build the Docker image with 'latest' and version tags
docker build -t atepeq/pr-reviewer:latest -t atepeq/pr-reviewer:%VERSION% .

REM Push the Docker images to Docker Hub
docker push atepeq/pr-reviewer:latest
docker push atepeq/pr-reviewer:%VERSION%

REM Note: Ensure you are logged in to Docker Hub before running this script.
REM Use 'docker login' to log in if you haven't already.
