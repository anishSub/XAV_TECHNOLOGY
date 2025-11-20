FROM python:3.11-slim-bookworm

# 1. install system utils first (rarely changes)
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-traditional && rm -rf /var/lib/apt/lists/*

# 2. python deps next
WORKDIR /app
COPY requirement.txt .
RUN pip install --no-cache-dir -r requirement.txt

# 3. code last
COPY . .
RUN python manage.py collectstatic --noinput
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]