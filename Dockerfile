FROM python:3.12.9-alpine3.21

COPY . /repbot
RUN pip install -e /repbot 

CMD ["python", "-m", "reputable_bot"]

