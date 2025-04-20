FROM python:3.13-alpine

WORKDIR /app

RUN apk add --no-cache gcc musl-dev libffi-dev py3-numpy openssl-dev

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["tail", "-f", "/dev/null"]