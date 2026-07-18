FROM python:3.12-slim


# libgl1-mesa-glx change to libl1

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*


# 3. Install uv inside the Docker container
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 4. Set the working directory
WORKDIR /app

# 5. Copy the uv lockfile and pyproject.toml first (Docker caching trick)
COPY pyproject.toml uv.lock ./

# 6. Install dependencies using uv (super fast!)
# RUN uv sync --frozen --no-dev
RUN uv sync --frozen

# 7. Copy the rest of your application code
COPY ./app ./app
COPY ./src ./src
COPY ./static ./static

# 8. Expose the port
EXPOSE 8000

# 9. Run the app using uv's environment
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000","--reload"]

