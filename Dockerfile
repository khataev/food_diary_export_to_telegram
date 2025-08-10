FROM python:3.11-slim

RUN pip install python-telegram-bot==20.3

WORKDIR /app

CMD ["bash"]
