FROM python:3.10

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip


RUN pip install --upgrade pip

RUN apt update && apt -qy install gcc libjpeg-dev libxslt-dev \
    libpq-dev libmariadb-dev libmariadb-dev-compat gettext cron openssh-client flake8 locales vim

RUN useradd -rms /bin/bash crm && chmod 777 /opt /run

WORKDIR /crm

RUN mkdir /crm/static && mkdir /crm/media && chown -R crm:crm /crm && chmod 755 /crm

COPY --chown=crm:crm . .

RUN pip install -r requirements.txt

RUN pip install gunicorn

USER crm

CMD ["gunicorn","-b","0.0.0.0:8001","crm_offices.wsgi:application"]

