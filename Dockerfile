FROM python:3.5.2-slim
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    gcc \
    gettext \
    libpq-dev \
    libjpeg-dev \
    libgeos-dev \
    binutils \
    libproj-dev \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

ADD requirements.txt /
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
