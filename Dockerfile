#
# example Dockerfile for https://docs.docker.com/engine/examples/postgresql_service/
#

FROM ubuntu:18.04
RUN apt-get update && apt-get install -y gnupg curl ca-certificates
RUN curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
# Add the PostgreSQL PGP key to verify their Debian packages.
# It should be the same key as https://www.postgresql.org/media/keys/ACCC4CF8.asc
#ENV APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=DontWarn
#RUN apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8

# Set a default number of database copies to be created.
ARG EXTRA_DB_COPIES=0
ARG SOURCE_BRANCH=master

# Add PostgreSQL's repository. Idocker-boomt contains the most recent stable release
#     of PostgreSQL, ``9.3``.
RUN echo "deb http://apt-archive.postgresql.org/pub/repos/apt/ bionic-pgdg main" > /etc/apt/sources.list.d/pgdg.list

# Install ``python-software-properties``, ``software-properties-common`` and PostgreSQL 9.3
#  There are some warnings (in red) that show up during the build. You can hide
#  them by prefixing each apt-get statement with DEBIAN_FRONTEND=noninteractive
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y software-properties-common postgresql-13 postgresql-client-13 postgresql-contrib-13 python3-pip libpq-dev

# Note: The official Debian and Ubuntu images automatically ``apt-get clean``
# after each ``apt-get``

ADD . .
#ADD data /data

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt

# Run the rest of the commands as the ``postgres`` user created by the ``postgres-13`` package when it was ``apt-get installed``
USER postgres

# Create a PostgreSQL role named ``docker`` with ``docker`` as the password and
# then create a database `docker` owned by the ``docker`` role.
# Note: here we use ``&&\`` to run commands one after the other - the ``\``
#       allows the RUN command to span multiple lines.
RUN    /etc/init.d/postgresql start &&\
    psql --command "CREATE USER tester WITH SUPERUSER PASSWORD 'tester';" &&\
    createdb -O tester fb_test &&\
    psql -d fb_test < schema.sql > /dev/null &&\
    python3 add-test_data.py &&\
    psql -d fb_test < triggers/multiple_seqs.sql &&\
    python3  multiple_databases.py ${EXTRA_DB_COPIES} ${SOURCE_BRANCH} &&\
    /etc/init.d/postgresql stop

# Adjust PostgreSQL configuration so that remote connections to the
# database are possible.
RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/13/main/pg_hba.conf

# And add ``listen_addresses`` to ``/etc/postgresql/13/main/postgresql.conf``
RUN echo "listen_addresses='*'" >> /etc/postgresql/13/main/postgresql.conf

# Turn on verbose logging for all SQL commands
RUN echo "log_destination = 'stderr'" >> /etc/postgresql/13/main/postgresql.conf
RUN echo "logging_collector = on" >> /etc/postgresql/13/main/postgresql.conf
RUN echo "log_statement = 'all'" >> /etc/postgresql/13/main/postgresql.conf

# https://pythonspeed.com/articles/faster-db-tests/
RUN echo "fsync = off" >> /etc/postgresql/13/main/postgresql.conf

# Do not add '\' in front of '\' to make '\\'
RUN echo "standard_conforming_strings = off" >> /etc/postgresql/13/main/postgresql.conf

# https://serverfault.com/questions/323356/postgres-connection-establishment-slow
RUN echo "log_hostname = off" >> /etc/postgresql/13/main/postgresql.conf

RUN echo "log_directory = '/var/log/postgresql'" >> /etc/postgresql/13/main/postgresql.conf

# Expose the PostgreSQL port
EXPOSE 5432

# Set the default command to run when starting the container
CMD ["/usr/lib/postgresql/13/bin/postgres", "-D", "/var/lib/postgresql/13/main", "-c", "config_file=/etc/postgresql/13/main/postgresql.conf"]