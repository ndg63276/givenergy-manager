FROM python:3.8-slim-buster
ADD . /app
ADD ./example_user_input.json /app/user_input.json
WORKDIR /app
CMD python serve.py 8001
EXPOSE 8001
