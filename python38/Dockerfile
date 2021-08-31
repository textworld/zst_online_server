FROM  ubuntu:20.04

RUN  sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list

RUN  apt-get clean

RUN apt-get update

RUN apt-get -y install gcc make zlib1g zlib1g-dev openssl libpcre3 libpcre3-dev

RUN apt-get -y install libbz2-dev libsqlite3-dev libxml2-dev libffi-dev libssl-dev libxslt1-dev

RUN apt-get -y install wget

RUN apt-get -y upgrade

RUN apt-get -y dist-upgrade

RUN apt-get -y install bzip2

RUN apt-get -y install python3-pip python3-dev

RUN wget https://www.python.org/ftp/python/3.8.10/Python-3.8.10.tar.xz

RUN tar -xvf Python-3.8.10.tar.xz

RUN cd Python-3.8.10 && ./configure && make -j 8 && make install

RUN pip install -U pip

RUN pip config set global.index-url http://mirrors.aliyun.com/pypi/simple

RUN pip config set install.trusted-host mirrors.aliyun.com

