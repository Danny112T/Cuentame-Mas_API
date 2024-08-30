FROM python:3.12-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set the working directory
WORKDIR /app

# Copy necessary files for dependency installation
ADD pyproject.toml /app/
ADD uv.lock /app/ 
ADD README.md /app/
# Run uv sync to install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

# Copy the rest of the application code
ADD . /app

# Run uv sync again to ensure everything is set up correctly
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-cache

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Run the FastAPI application by default
# Uses `fastapi dev` to enable hot-reloading when the `watch` sync occurs
# Uses `--host 0.0.0.0` to allow access from outside the container
CMD ["fastapi", "run","--port", "8000", "--host", "0.0.0.0"]