FROM  ubuntu:20.04
ENV TZ=Asia/Shanghai

RUN  sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list \
     && apt-get update \
     && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
     && apt-get install tzdata \
     && apt-get -y install gcc make zlib1g zlib1g-dev openssl libpcre3 libpcre3-dev \
     && apt-get -y install libbz2-dev libsqlite3-dev libxml2-dev libffi-dev libssl-dev libxslt1-dev \
     && apt-get -y install wget bzip2 python3-pip python3-dev  python3-pip \
     && apt-get -y upgrade \
     && apt-get -y dist-upgrade \
     && apt-get clean \
     && apt-get autoclean \
     && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN wget https://image.textworld.cn/Python-3.8.10.tar.xz \
    && tar -xvf Python-3.8.10.tar.xz \
    && cd Python-3.8.10 && ./configure && make -j 8 && make install \
    && cd ../ \
    && rm -rf ./Python-3.8.10 \
    && rm -rf ./Python-3.8.10.tar.xz


RUN pip install -U pip -i http://mirrors.aliyun.com/pypi/simple \
    && pip config set global.index-url http://mirrors.aliyun.com/pypi/simple \
    && pip config set install.trusted-host mirrors.aliyun.com


