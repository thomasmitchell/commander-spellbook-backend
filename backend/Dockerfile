###########
# BUILDER #
###########

# pull official base image
FROM alpine:edge as builder

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk --update add --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing gcc pypy3 musl-dev postgresql-dev && ln -sf pypy3 /usr/bin/pypy

# pip
RUN pypy -m ensurepip && pypy -m pip install --upgrade pip wheel

# install dependencies
COPY ./requirements.txt .
RUN echo -e '\n\
gunicorn\n\
psycopg2\n' >> requirements.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

# lint
RUN pip install flake8
COPY . .
RUN pypy -m flake8 --ignore=E501,F401,E128,W601 .


#########
# FINAL #
#########

# pull official base image
FROM alpine:edge

# create directory for the app user
RUN mkdir -p /home/app

# create the app user
RUN addgroup -S app && adduser -S app -G app

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir -p $APP_HOME/staticfiles
WORKDIR $APP_HOME

# install dependencies
RUN apk --no-cache --update add --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing libpq pypy3 && ln -sf pypy3 /usr/bin/pypy
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pypy -m ensurepip && pypy -m pip install --no-cache /wheels/*

# copy project
COPY . $APP_HOME

# chown all the files to the app user
RUN chown -R app:app $APP_HOME

# change to the app user
USER app

ARG SECRET_KEY
ENV SECRET_KEY=${SECRET_KEY}
ENV DJANGO_SETTINGS_MODULE=backend.production_settings
# run entrypoint.prod.sh
RUN echo -e 'pypy manage.py collectstatic --no-input --clear\n\
sleep 3\n\
pypy manage.py migrate --noinput\n\
pypy manage.py clean_jobs\n\
pypy manage.py export_variants\n\
pypy -m gunicorn backend.wsgi:application --bind 0.0.0.0:8000\n' > entrypoint.prod.sh
EXPOSE 8000
ENTRYPOINT ["/bin/sh", "entrypoint.prod.sh"]
