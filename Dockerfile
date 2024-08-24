FROM python:3.11.9-slim-bullseye

WORKDIR /work

# Install poetry
RUN pip install --no-cache-dir poetry

# Copy only pyproject.toml and poetry.lock first to leverage Docker cache
COPY pyproject.toml poetry.lock ./

# Install dependencies using poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --no-cache

# Copy the rest of the application
COPY . .

# Output README.md as the default command
CMD [ "cat", "README.md" ]
