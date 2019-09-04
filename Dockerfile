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

# Add PostgreSQL's repository. Idocker-boomt contains the most recent stable release
#     of PostgreSQL, ``9.3``.
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ bionic-pgdg main" > /etc/apt/sources.list.d/pgdg.list

# Install ``python-software-properties``, ``software-properties-common`` and PostgreSQL 9.3
#  There are some warnings (in red) that show up during the build. You can hide
#  them by prefixing each apt-get statement with DEBIAN_FRONTEND=noninteractive
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y software-properties-common postgresql-10 postgresql-client-10 postgresql-contrib-10 python3-pip

# Note: The official Debian and Ubuntu images automatically ``apt-get clean``
# after each ``apt-get``

ADD add-test_data.py .
ADD schema.sql .
ADD requirements.txt .
ADD data /data

RUN pip3 install -r requirements.txt

# Run the rest of the commands as the ``postgres`` user created by the ``postgres-10`` package when it was ``apt-get installed``
USER postgres

# Create a PostgreSQL role named ``docker`` with ``docker`` as the password and
# then create a database `docker` owned by the ``docker`` role.
# Note: here we use ``&&\`` to run commands one after the other - the ``\``
#       allows the RUN command to span multiple lines.
RUN    /etc/init.d/postgresql start &&\
    psql --command "CREATE USER tester WITH SUPERUSER PASSWORD 'tester';" &&\
    createdb -O tester fb_test &&\
    psql -d fb_test < schema.sql > /dev/null &&\
    python3 add-test_data.py

# Adjust PostgreSQL configuration so that remote connections to the
# database are possible.
RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/10/main/pg_hba.conf

# And add ``listen_addresses`` to ``/etc/postgresql/10/main/postgresql.conf``
RUN echo "listen_addresses='*'" >> /etc/postgresql/10/main/postgresql.conf

# Turn on verbose logging for all SQL commands
RUN echo "log_destination = 'stderr'" >> /etc/postgresql/10/main/postgresql.conf
RUN echo "logging_collector = on" >> /etc/postgresql/10/main/postgresql.conf
RUN echo "log_statement = 'all'" >> /etc/postgresql/10/main/postgresql.conf
RUN echo "log_directory = '/var/log/postgresql'" >> /etc/postgresql/10/main/postgresql.conf

# Expose the PostgreSQL port
EXPOSE 5432

# Set the default command to run when starting the container
CMD ["/usr/lib/postgresql/10/bin/postgres", "-D", "/var/lib/postgresql/10/main", "-c", "config_file=/etc/postgresql/10/main/postgresql.conf"]