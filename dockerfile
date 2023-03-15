FROM ubuntu:22.04
RUN apt-get update
RUN apt-get install -y python3 python3-pip nano
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir requests PyP100
ADD . /app
ADD ./example_user_input.json /app/user_input.json
WORKDIR /app
CMD python3 serve.py 8001
EXPOSE 8001
