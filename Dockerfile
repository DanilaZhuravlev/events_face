FROM python:3.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN pip install --no-cache-dir uv

RUN uv venv

ENV PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml uv.lock* ./

RUN uv pip compile pyproject.toml --output-file=requirements.txt

RUN uv pip sync requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "--worker-class=gevent", "--workers=4", "--bind", "0.0.0.0:8000", "src.core.wsgi:application"]