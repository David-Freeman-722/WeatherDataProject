ARG AIRFLOW_VERSION=2.9.2
ARG PYTHON_VERSION=3.11    
ARG REQUIREMENTS_FILE=requirements.txt

FROM apache/airflow:${AIRFLOW_VERSION}-python${PYTHON_VERSION}
LABEL maintainer="The Apache Software Foundation"

# Set up Constraint URL for stable dependency resolution
ENV CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

# Install system dependencies (required for psycopg2/Postgres provider)
USER root
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
USER ${AIRFLOW_UID}

# Install dependencies from requirements.txt using constraints
COPY ${REQUIREMENTS_FILE} /requirements.txt
RUN if [ -f "/requirements.txt" ]; then \
    pip install --no-cache-dir -r /requirements.txt --constraint "${CONSTRAINT_URL}"; \
    fi