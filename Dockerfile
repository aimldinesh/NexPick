# -----------------------------
# ✅ Base Image
# -----------------------------
FROM python:3.10-slim

# -----------------------------
# ✅ Environment Variables
# -----------------------------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# -----------------------------
# ✅ Set Work Directory
# -----------------------------
WORKDIR /app

# -----------------------------
# ✅ Install System Dependencies
# -----------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# ✅ Copy Project Files
# -----------------------------
COPY . .

# -----------------------------
# ✅ Install Python Dependencies
# -----------------------------
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -e .

# -----------------------------
# ✅ Expose Port
# -----------------------------
EXPOSE 5000

# -----------------------------
# ✅ Run the App
# -----------------------------
CMD ["python", "app.py"]
