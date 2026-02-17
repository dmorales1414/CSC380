# Uses 3.12 or below slim python image as base to use psycopg2 from requirements.txt
# Because of the compatibility issues with psycopg2 and python 3.14+ (does not ship wheels for 3.14+)
FROM python:3.12-slim

WORKDIR /Retro_Video_Game

# Environment Variables (Wasn't sure how to set these up, so asked ChatGPT for help)
ENV APP_ENV=production
ENV DB_HOST=localhost
ENV DB_PORT=5000
ENV DB_NAME=retro_game_api


# Dependencies (Installation)
COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Application Code
COPY ./email_service/wait_for_kafka.py .

COPY . .

# Exposes the port the API runs on
EXPOSE 5000

# Run the API
CMD ["sh", "-c", "python wait_for_kafka.py && python app.py"]