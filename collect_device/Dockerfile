FROM python:3.10-slim

WORKDIR /app

# Cài đặt git và các dependency
RUN apt-get update && apt-get install -y git && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Cài đặt Python dependencies
RUN pip install --no-cache-dir fastapi uvicorn psutil py-cpuinfo gitpython

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]