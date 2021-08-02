from .base import *
import os

LOG_DIR = os.path.join("/var/log/zst_online_server", "log")

# 基本配置，可以复用的
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {  # 定义了两种日志格式
        "verbose": {  # 标准
            "format": "%(levelname)s %(asctime)s %(module)s "
                      "%(process)d %(thread)d %(message)s"
        },
        'simple': {  # 简单
            'format': '[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d]%(message)s'
        },
    },
    "handlers": {  # 定义了三种日志处理方式
        'file': {  # Info级别以上保存到日志文件
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件，根据文件大小自动切
            'filename': os.path.join(LOG_DIR, "info.log"),  # 日志文件
            'maxBytes': 1024 * 1024 * 10,  # 日志大小 10M
            'backupCount': 2,  # 备份数为 2
            'formatter': 'simple',  # 简单格式
            'encoding': 'utf-8',
        },
        "console": {  # 打印到终端console
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"level": "INFO", "handlers": ["console"]},
    "loggers": {
        'django': {
            'handlers': ['console', 'file'],
            'propagate': True,
        },
    },
}
