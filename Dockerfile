#Grab the latest alpine image
FROM python:3.6
ENV PYTHONUNBUFFERED 1
# Install python and pip
# RUN apk add --no-cache --update python3 py3-pip bash
# ADD ./webapp/requirements.txt /tmp/requirements.txt

# Install dependencies

# Add our code

RUN mkdir /opt/webapp/
WORKDIR /opt/webapp

ADD webapp .

RUN pip install --no-cache-dir -q -r requirements.txt

# Expose is NOT supported by Heroku
# EXPOSE 5000

# Run the image as a non-root user
RUN adduser myuser
USER myuser

# Run the app.  CMD is required to run on Heroku
# $PORT is set by Heroku
CMD  gunicorn --bind 0.0.0.0:$PORT --reload wsgi

