FROM ubuntu:22.04
RUN apt-get update
RUN apt-get install -y python3 python3-pip nano cron
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir requests PyP100
ADD . /app
ADD ./example_user_input.json /app/user_input.json
ADD ./givenergy_manager.cron /etc/cron.d/givenergy_manager.cron
RUN chmod 0644 /etc/cron.d/givenergy_manager.cron
RUN crontab /etc/cron.d/givenergy_manager.cron
RUN touch /var/log/cron.log

WORKDIR /app
CMD /app/runner.sh
EXPOSE 8001
