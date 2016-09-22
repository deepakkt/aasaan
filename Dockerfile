FROM python:3.4.5-wheezy
MAINTAINER deepak.kumaran@ishafoundation.org
RUN apt-get -y update
RUN apt-get -y install python3-dev python3-setuptools
RUN apt-get -y install libjpeg8-dev libfreetype6-dev zlib1g-dev libjpeg-dev
RUN apt-get -y install libpq-dev python3-dev python-dev
RUN apt-get -y install libffi-dev
RUN apt-get -y install memcached libmemcached-dev
RUN apt-get -y install zlib1g-dev
RUN apt-get -y install supervisor
RUN mkdir /usr/aasaan
RUN mkdir /usr/aasaan/src
RUN mkdir /var/www && mkdir /var/www/aasaan
RUN mkdir /var/www/aasaan/media && mkdir /var/www/aasaan/static
COPY requirements.txt /usr/aasaan/src
WORKDIR /usr/aasaan/src
RUN pip install -r requirements.txt
COPY . /usr/aasaan/src
COPY deploy/aasaan_start_docker /usr/local/bin
COPY deploy/aasaan_worker_start_docker /usr/local/bin
COPY deploy/supervisord_docker.conf /etc/supervisor/conf.d/supervisord.conf
CMD ["/usr/bin/supervisord"]