FROM  python:v3.8.10

RUN apt-get update \
    && apt-get install -y libmysqlclient-dev  libldap2-dev libsasl2-dev libssl-dev \
    && apt-get install -y --no-install-recommends git \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

VOLUME ["/web/zst_online_server"]

WORKDIR /web

COPY requirements.txt ./

RUN pip3 install -r requirements.txt

COPY vsapp_uwsgi.ini ./
COPY celeryconf/celeryd /etc/init.d/
COPY celeryconf/celerybeat /etc/init.d/
COPY celeryd /etc/default/
COPY run_web.sh ./
RUN chmod 777 run_web.sh \
    && chmod 777 /etc/init.d/celeryd \
    && chmod 777 /etc/init.d/celerybeat \
    && chmod 640 /etc/default/celeryd

EXPOSE 8000
# CMD ["./run_web.sh"]