FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH="/app/tg_bot:${PYTHONPATH}"

ENV PYTHONUNBUFFERED=1
CMD ["python", "-m", "tg_bot.bot"]
