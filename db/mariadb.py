import logging
import MySQLdb
import json

logging.basicConfig(format='%(asctime)s-%(levelname)s-%(name)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


def get_connection(host, port, db_name, user, password):

    return MySQLdb.connect(host=host, user=user, passwd=password, db=db_name, port=port,
                           use_unicode=True, charset='utf8')


def write_files_data(file_data_tuples, connection):

    batch_size = 100

    if batch_size > len(file_data_tuples):
        batch_size = len(file_data_tuples)

    batch_index = 0

    cursor = connection.cursor()
    while batch_index < len(file_data_tuples):
        batch = file_data_tuples[batch_index:batch_index+batch_size]
        statement = 'INSERT INTO `image_files` (`name`, `path`, `url`) VALUES (%s, %s, %s);'
        cursor.executemany(statement, batch)
        batch_index += batch_size

    connection.commit()


def get_files_data(offset, limit, connection):

    statement = 'SELECT * FROM `image_files` WHERE `id` >= %s AND `id` < %s'
    values = (offset + 1, offset + 1 + limit)

    cursor = connection.cursor()
    cursor.execute(statement, values)
    result = cursor.fetchall()
    cursor.close()
    return result


def get_all_files_data(connection):

    statement = 'SELECT * FROM `image_files`'

    cursor = connection.cursor()
    cursor.execute(statement)
    result = cursor.fetchall()
    cursor.close()
    return result


def get_all_file_paths(connection):

    statement = 'SELECT `path` FROM `image_files`'

    cursor = connection.cursor()
    cursor.execute(statement)
    result = cursor.fetchall()
    cursor.close()
    return result


def write_file_features(image_id, features, connection):

    statement = 'INSERT IGNORE INTO `image_features` (`image_id`, `features`) VALUES (%s, %s);'
    values = (image_id, json.dumps(features.tolist()))

    cursor = connection.cursor()
    cursor.execute(statement, values)
    cursor.close()

    connection.commit()


def get_all_file_features(connection):
    statement = 'SELECT * FROM `image_features`;'

    cursor = connection.cursor()
    cursor.execute(statement)
    result = cursor.fetchall()
    cursor.close()

    return result


def get_every_nth_index_for_table(connection, n, tablename):

    statement = f"SELECT * FROM (SELECT @row := @row +1 AS row_num " \
                f"FROM (SELECT @row :=0) r, {tablename}) ranked WHERE row_num MOD %s = 1"

    values = (n,)

    cursor = connection.cursor()
    cursor.execute(statement, values)
    result = cursor.fetchall()
    cursor.close()

    return [int(i[0]) for i in result]


def get_every_nth_file_feature(connection, n):
    indices = get_every_nth_index_for_table(connection, n, "image_features")

    format_string = ','.join(['%s'] * len(indices))
    statement = f"SELECT * FROM image_features WHERE image_id in ({format_string})"

    cursor = connection.cursor()
    cursor.execute(statement, indices)
    result = cursor.fetchall()
    cursor.close()

    return result


def write_uncompressed_file_features(image_id, features, connection):

    statement = 'INSERT IGNORE INTO `image_features_uncompressed` (`image_id`, `features`) VALUES (%s, %s);'
    values = (image_id, json.dumps(features.tolist()))

    cursor = connection.cursor()
    cursor.execute(statement, values)
    cursor.close()

    connection.commit()


def get_all_file_features_uncompressed(connection):
    statement = 'SELECT * FROM `image_features_uncompressed`;'

    cursor = connection.cursor()
    cursor.execute(statement)
    result = cursor.fetchall()
    cursor.close()

    return result


def get_every_nth_file_feature_uncompressed(connection, n):
    indices = get_every_nth_index_for_table(connection, n, "image_features_uncompressed")

    format_string = ','.join(['%s'] * len(indices))
    statement = f"SELECT * FROM image_features_uncompressed WHERE image_id in ({format_string})"

    cursor = connection.cursor()
    cursor.execute(statement, indices)
    result = cursor.fetchall()
    cursor.close()

    return result


def get_image_count(connection):
    statement = 'SELECT count(*) FROM `image_files`;'

    cursor = connection.cursor()
    cursor.execute(statement)
    result = cursor.fetchone()
    cursor.close()

    return result[0]


def get_images_with_neighbours(connection):
    cursor = connection.cursor()

    statement = "SELECT image_id FROM image_neighbours;"
    cursor.execute(statement)
    compressed = cursor.fetchall()

    statement = "SELECT image_id FROM image_neighbours_uncompressed;"
    cursor.execute(statement)
    uncompressed = cursor.fetchall()

    cursor.close()

    return [i[0] for i in compressed], [i[0] for i in uncompressed]


def get_feature_count(connection):
    statement = 'SELECT count(*) FROM `image_features`;'

    cursor = connection.cursor()
    cursor.execute(statement)
    result = cursor.fetchone()
    cursor.close()

    return result[0]


def get_features_for_id(id, connection):
    statement = 'SELECT * FROM `image_features` WHERE `image_id` = %s;'

    cursor = connection.cursor()
    cursor.execute(statement, (str(id),))
    result = cursor.fetchone()
    cursor.close()

    return result


def write_neighbours(image_id, neighbours, connection):
    statement = 'INSERT IGNORE INTO `image_neighbours` (`image_id`, `neighbours`) ' \
                'VALUES (%s, %s);'

    values = (str(image_id), json.dumps(neighbours))

    cursor = connection.cursor()
    cursor.execute(statement, values)
    cursor.close()

    connection.commit()


def write_uncompressed_neighbours(image_id, neighbours, connection):
    statement = 'INSERT IGNORE INTO `image_neighbours_uncompressed` (`image_id`, `neighbours`) ' \
                'VALUES (%s, %s);'

    values = (str(image_id), json.dumps(neighbours))

    cursor = connection.cursor()
    cursor.execute(statement, values)
    cursor.close()

    connection.commit()


def get_image_and_neigbours_by_id(image_id, connection):
    statement = 'SELECT ' \
                'image_files.name, ' \
                'image_files.url, ' \
                'image_neighbours.neighbours, ' \
                'image_neighbours_uncompressed.neighbours ' \
                'FROM image_files, image_neighbours, image_neighbours_uncompressed ' \
                'WHERE image_files.`id`=%s ' \
                'AND `image_neighbours`.`image_id`=`image_files`.`id` ' \
                'AND `image_neighbours_uncompressed`.`image_id`=`image_files`.`id`;'

    try:
        cursor = connection.cursor()
        cursor.execute(statement, (image_id,))
        (image_name, image_url, neighbours_data, neighbours_uncompressed_data) = cursor.fetchone()
        parsed_json = json.loads(neighbours_data)

        neighbours = []
        for neighbour in parsed_json:

            statement = 'SELECT image_files.name, image_files.url FROM image_files WHERE image_files.id = %s;'
            cursor.execute(statement, (neighbour[0],))
            (neighbour_name, neighbour_url) = cursor.fetchone()

            neighbours.append({
                'id': neighbour[0],
                'distance': neighbour[1],
                'name': neighbour_name,
                'url': neighbour_url
            })

        parsed_uncompressed_json = json.loads(neighbours_uncompressed_data)
        neighbours_uncompressed = []
        for neighbour in parsed_uncompressed_json:

            statement = 'SELECT image_files.name, image_files.url FROM image_files WHERE image_files.id = %s;'
            cursor.execute(statement, (neighbour[0],))
            (neighbour_name, neighbour_url) = cursor.fetchone()

            neighbours_uncompressed.append({
                'id': neighbour[0],
                'distance': neighbour[1],
                'name': neighbour_name,
                'url': neighbour_url
            })
        cursor.close()
        return image_name, image_url, neighbours, neighbours_uncompressed

    except TypeError:
        logger.debug('No result for:')
        logger.debug(statement)
        logger.debug(image_id)

        return []
