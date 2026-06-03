FROM python:3.11-slim
ENV PIP_INDEX_URL=https://mirror-pypi.runflare.com/simple
ENV PIP_TRUSTED_HOST=mirror-pypi.runflare.com
WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "app.main"]
