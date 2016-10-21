#!/bin/sh

/usr/bin/redis-server /etc/redis/redis.conf
exec .venv/bin/python -u -m heropets-webserver.server
