FROM python:3.10

COPY ./ /home/convey/

WORKDIR /home/convey/

RUN apt-get update

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["bash", "-c", "python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8080"]