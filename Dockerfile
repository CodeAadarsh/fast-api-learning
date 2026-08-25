FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./

RUN uv sync

COPY . .

RUN uv sync 

CMD ["uv","run","uvicorn","main:app", "--host","0.0.0.0"]
