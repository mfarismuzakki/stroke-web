FROM python:3.9

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
# install python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /

# running migrations
# RUN python manage.py migrate

EXPOSE 5005

RUN chmod +x /run.sh
RUN python manage.py collectstatic --noinput

# gunicorn
# RUN /bin/bash -c '/run.sh' 

# ENTRYPOINT ["/run.sh"]
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]
# CMD ["/run.sh"]
