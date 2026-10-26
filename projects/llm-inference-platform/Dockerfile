# SPDX-FileCopyrightText: 2026 Kumar Raja Annamreddi
# SPDX-License-Identifier: Apache-2.0
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --uid 10001 --create-home gateway
COPY inference ./inference
COPY LICENSE NOTICE THIRD_PARTY_NOTICES.md ./
COPY third_party ./third_party
USER 10001:10001
EXPOSE 8000
# One worker: admission limits are process-local.
CMD ["uvicorn", "inference.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--no-access-log"]
