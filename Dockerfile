FROM python:3.10

COPY ./ /home/convey/

WORKDIR /home/convey/

RUN apt-get update

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["bash", "-c", "python3 manage.py migrate && gunicorn config.wsgi.deploy:application --bind 0.0.0.0:8080 --timeout=30"]