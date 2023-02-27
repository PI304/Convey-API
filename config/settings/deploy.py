from .base import *

# DEBUG = False
ALLOWED_HOSTS = [
    "13.125.243.32",
    "localhost",
    "127.0.0.1",
]  # 인스턴스 IPv4 기반 퍼블릭 DNS 주소 or 퍼블릭 IP

WSGI_APPLICATION = "config.wsgi.deploy.application"
