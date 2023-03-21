FROM ubuntu:22.04
RUN apt-get update
RUN apt-get install -y python3 python3-pip nano cron
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir requests PyP100
ADD . /app
ADD ./cgi-bin/example_user_input.json /app/cgi-bin/user_input.json
RUN ln -fs /app/cgi-bin/user_input.json /app/user_input.json
# Fix bug with PyP100 library
RUN sed -i 's/"requestTimeMils": 0/"requestTimeMils": int(round(time.time() * 1000))/g' /usr/local/lib/python3.10/dist-packages/PyP100/PyP100.py
ADD ./givenergy_manager.cron /etc/cron.d/givenergy_manager.cron
RUN chmod 0644 /etc/cron.d/givenergy_manager.cron
RUN crontab /etc/cron.d/givenergy_manager.cron
RUN touch /var/log/cron.log

WORKDIR /app
CMD /app/runner.sh
EXPOSE 8001
