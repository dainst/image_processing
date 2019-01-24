FROM mariadb

ENV REFRESHED_AT 2018-06-27
LABEL maintainer="Deutsches Archäologisches Institut: dev@dainst.de"

ARG DB_NAME
ARG DB_ROOT_PW
ARG DB_USER
ARG DB_PASSWORD

RUN apt-get update
RUN apt-get install -y locales
RUN rm -rf /var/lib/apt/lists/* $
RUN localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG en_US.utf8
ENV MYSQL_ROOT_PASSWORD $DB_ROOT_PW

RUN echo "Creating main-DB-User ..."
RUN echo "CREATE database if not exists $DB_NAME CHARACTER SET utf8 COLLATE utf8_general_ci; \
        GRANT ALL ON $DB_NAME.* TO '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASSWORD' WITH GRANT OPTION ; \
        GRANT ALL ON $DB_NAME.* TO '$DB_USER'@'%' IDENTIFIED BY '$DB_PASSWORD' WITH GRANT OPTION ; \
        FLUSH PRIVILEGES ;" > /docker-entrypoint-initdb.d/000000_create_db_and_user.sql

COPY table_setup/image_files.sql /docker-entrypoint-initdb.d/000001_image_files.sql
COPY table_setup/image_features.sql /docker-entrypoint-initdb.d/000002_image_feature.sql
COPY table_setup/image_neighbours.sql /docker-entrypoint-initdb.d/000003_image_neighbours.sql

RUN echo "USE $DB_NAME;\n$(cat /docker-entrypoint-initdb.d/000001_image_files.sql)" > /docker-entrypoint-initdb.d/000001_image_files.sql
RUN echo "USE $DB_NAME;\n$(cat /docker-entrypoint-initdb.d/000002_image_feature.sql)" > /docker-entrypoint-initdb.d/000002_image_feature.sql
RUN echo "USE $DB_NAME;\n$(cat /docker-entrypoint-initdb.d/000003_image_neighbours.sql)" > /docker-entrypoint-initdb.d/000003_image_neighbours.sql

EXPOSE 3306
