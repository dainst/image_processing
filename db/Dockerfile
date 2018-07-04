FROM mariadb

ENV REFRESHED_AT 2018-06-27
LABEL maintainer="Deutsches Archäologisches Institut: dev@dainst.de"

ENV MYSQL_ROOT_PASSWORD root
ENV MYSQL_DATABASE_NAME image_processing_db
ENV MYSQL_USER_NAME main_user
ENV MYSQL_USER_PASSWORD pwd

RUN apt-get update
RUN apt-get install -y locales
RUN rm -rf /var/lib/apt/lists/* $
RUN localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG en_US.utf8

RUN echo "Creating main-DB-User ..."
RUN echo "CREATE database if not exists $MYSQL_DATABASE_NAME CHARACTER SET utf8 COLLATE utf8_general_ci; \
        GRANT ALL ON $MYSQL_DATABASE_NAME.* TO '$MYSQL_USER_NAME'@'localhost' IDENTIFIED BY '$MYSQL_USER_PASSWORD' WITH GRANT OPTION ; \
        GRANT ALL ON $MYSQL_DATABASE_NAME.* TO '$MYSQL_USER_NAME'@'%' IDENTIFIED BY '$MYSQL_USER_PASSWORD' WITH GRANT OPTION ; \
        FLUSH PRIVILEGES ;" > /docker-entrypoint-initdb.d/000_create_db_and_user.sql

COPY table_setup/image_names.sql /docker-entrypoint-initdb.d/001_image_names.sql
COPY table_setup/image_features.sql /docker-entrypoint-initdb.d/002_image_feature.sql
COPY table_setup/image_neighbours.sql /docker-entrypoint-initdb.d/003_image_neighbours.sql

EXPOSE 3306
