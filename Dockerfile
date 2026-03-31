FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY main.py parsed_documentation.py ./
COPY data/ ./data/

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["python", "main.py"]
CMD ["data/index.json"]
