FROM python:3.12-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends git \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
COPY task/repo /workspace/repo
WORKDIR /workspace/repo

RUN pip install --no-cache-dir -e . \
 && pip install --no-cache-dir pytest pytz simplejson dateparser

WORKDIR /workspace
