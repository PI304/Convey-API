from .base import *

DEBUG = False
ALLOWED_HOSTS = ["3.34.67.68", "api.convey.works", "convey.works"]

WSGI_APPLICATION = "config.wsgi.deploy.application"
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
