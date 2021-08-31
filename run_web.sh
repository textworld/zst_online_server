#!/bin/bash
# 启动celery的异步任务与定时任务
/etc/init.d/celeryd start
/etc/init.d/celerybeat start
# 启动uwsgi
uwsgi --ini vsapp_uwsgi.ini