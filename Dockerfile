FROM python:3-alpine

ENV FLASK_APP=roster-reminder.py

WORKDIR /app
RUN mkdir /app/db

COPY requirements.txt /app
COPY roster-reminder.py /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENTRYPOINT [ "flask"]
CMD [ "run", "--host", "0.0.0.0" ]