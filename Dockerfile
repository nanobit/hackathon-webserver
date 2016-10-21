FROM ubuntu

# Expose ports
EXPOSE 5000

RUN apt-get update && \
    apt-get install -y python-virtualenv redis-server \
    libyaml-0-2 libffi6 libssl1.0.0 libzmq5 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install from pip
# ADD pip/pip.conf /root/.pip/pip.conf
WORKDIR /root
RUN virtualenv .venv && .venv/bin/pip install -U pip && .venv/bin/pip install -U "pip==8.1.2" "setuptools==25.1.6"
ADD setup.py /root/setup.py
ADD heropets-webserver /root/heropets-webserver
RUN .venv/bin/pip install -e .

ADD ./docker/start.sh /root/start.sh

CMD ["/root/start.sh"]