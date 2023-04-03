from .base import *

DEBUG = False
ALLOWED_HOSTS = ["3.34.67.68", "api.convey.works", "convey.works"]

WSGI_APPLICATION = "config.wsgi.deploy.application"
