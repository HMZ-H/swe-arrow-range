FROM python:3.12-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends git \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
COPY task/repo /workspace/repo
WORKDIR /workspace/repo

# A clean git history so the grader can diff and reset the working tree.
RUN git init -q -b main \
 && git config user.email task@local \
 && git config user.name task \
 && git add -A \
 && git commit -q -m "arrow at da6ed8c~1"

RUN pip install --no-cache-dir -e . \
 && pip install --no-cache-dir pytest pytz simplejson dateparser

WORKDIR /workspace
