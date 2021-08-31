FROM  python:v3.8.10

RUN apt-get update \
    && apt-get install -y libmysqlclient-dev  libldap2-dev libsasl2-dev libssl-dev \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

VOLUME ["/web/zst_online_server"]

WORKDIR /web

COPY requirements.txt ./

RUN pip install -U pip -i http://mirrors.aliyun.com/pypi/simple

RUN pip config set global.index-url http://mirrors.aliyun.com/pypi/simple

RUN pip config set install.trusted-host mirrors.aliyun.com

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