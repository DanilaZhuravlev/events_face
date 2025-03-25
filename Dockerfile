FROM python:3.13

WORKDIR /app

RUN pip install uv

# Создание и активация виртуального окружения
RUN uv venv
ENV PATH="/app/.venv/bin:$PATH"


COPY pyproject.toml uv.lock ./

RUN uv pip install -r uv.lock

# Копирование остального кода приложения
COPY . .

EXPOSE 8000

# Запуск приложения
CMD ["gunicorn", "--worker-class=gevent", "--workers=4", "--bind", "0.0.0.0:8000", "src.core.wsgi:application"]