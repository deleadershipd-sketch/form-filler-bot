# استخدام صورة Python رسمية مع دعم متصفح
FROM python:3.11-slim

# تثبيت Chromium ومشغل السيلينيوم
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# تعيين متغيرات البيئة لاستخدامها في الكود
ENV CHROME_PATH=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# نسخ ملفات المشروع
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# تشغيل التطبيق
CMD ["python", "web_app/app.py"]
