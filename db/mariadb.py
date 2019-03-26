import logging
import MySQLdb
import json
import numpy

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


def write_file_names(file_list, connection):
    cursor = connection.cursor()    

    batch_size = 10000

    if batch_size > len(file_list):
        batch_size = len(file_list)

    batch_index = 0

    cursor = connection.cursor()

    while batch_index < len(file_list):

        batch = file_list[batch_index:batch_index + batch_size]

        statement = 'INSERT IGNORE INTO `image_names` (`file_name`) VALUES\n'
        for idx, image_name in enumerate(batch):
            statement += f'("{image_name}"),\n'

        statement = statement[0:-2]
        cursor.execute(statement)

        batch_index += batch_size

    connection.commit()
    cursor.close()


def is_known_file(file_name, connection):
    statement = 'SELECT * FROM `image_names` where `file_name`="' + file_name + '";'

    cursor = connection.cursor()
    cursor.execute(statement)
    result = cursor.fetchone()
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


# def write_batch_of_compressed_features(image_ids, features_list, connection):
#
#     statement = 'INSERT IGNORE INTO `image_features_compressed` (`image_id`, `features`) VALUES'
#
#     for idx, image_id in enumerate(image_ids):
#         if idx != 0:
#             statement += ','
#         statement += '("' + str(image_id) + '", "' + json.dumps(features_list[idx].tolist()) + '")'
#     statement += ';'
#
#     cursor = connection.cursor()
#     cursor.execute(statement)
#     connection.commit()
#     cursor.close()


def get_image_count(connection):
    statement = 'SELECT count(*) FROM `image_files`;'

    cursor = connection.cursor()
    cursor.execute(statement)
    result = cursor.fetchone()
    cursor.close()

    return result[0]


def get_feature_count(connection):
    statement = 'SELECT count(*) FROM `image_features`;'

    cursor = connection.cursor()
    cursor.execute(statement)
    result = cursor.fetchone()
    cursor.close()

    return result[0]


def get_features_for_id(id, connection):
    statement = 'SELECT * FROM `image_features` WHERE `image_id` = ' + str(id) + ';'

    cursor = connection.cursor()
    cursor.execute(statement)
    result = cursor.fetchone()
    cursor.close()

    return result


def get_features_by_name(file_name, connection):
    statement = 'SELECT * FROM `image_names`, `image_features` WHERE `image_names`.`file_name` = "' + file_name + '" AND `image_names`.`id`=`image_features`.`image_id`;'

    cursor = connection.cursor()
    cursor.execute(statement)
    result = cursor.fetchone()
    cursor.close()

    return result


def _get_feature_batch_data(offset, size, connection):
    statement = 'SELECT * FROM `image_features` WHERE `image_id` >= ' + str(offset) + ' AND `image_id` < ' + str(offset + size) + ';'

    cursor = connection.cursor()
    cursor.execute(statement)
    result = cursor.fetchall()
    cursor.close()

    return result


def get_feature_batch(offset, batch_size, connection):
    batch_data = _get_feature_batch_data(offset, batch_size, connection)
    batch_feature_vectors = []
    batch_feature_ids = []
    for (image_id, feature_string) in batch_data:
        batch_feature_vectors.append(json.loads(feature_string))
        batch_feature_ids.append(image_id)

    matrix = numpy.array(batch_feature_vectors)

    return batch_feature_ids, matrix


def _get_compressed_feature_batch_data(offset, size, connection):
    statement = 'SELECT * FROM `image_features_compressed` WHERE `image_id` >= ' + str(offset) + ' AND `image_id` < ' + str(offset + size) + ';'

    cursor = connection.cursor()
    cursor.execute(statement)
    result = cursor.fetchall()
    cursor.close()

    return result


def get_compressed_feature_batch(offset, batch_size, connection):
    batch_data = _get_compressed_feature_batch_data(offset, batch_size, connection)
    batch_feature_vectors = []
    batch_feature_ids = []
    for (image_id, feature_string) in batch_data:
        batch_feature_vectors.append(json.loads(feature_string))
        batch_feature_ids.append(image_id)

    matrix = numpy.array(batch_feature_vectors)

    return batch_feature_ids, matrix


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


# def get_image_name(image_id, connection):
#     statement = 'SELECT `image_names`.`file_name` FROM `image_names` WHERE `image_names`.`id`=%s;'
#
#     try:
#         cursor = connection.cursor()
#         cursor.execute(statement, (image_id,))
#         image_name = cursor.fetchone()
#         cursor.close()
#         return image_name
#     except TypeError:
#         logger.debug(statement)
#         logger.debug(image_id)


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


def get_image_data(image_id, connection):
    statement = f'SELECT `image_names`.`id`, `image_names`.`file_name`, `image_features`.`features` ' \
        f'FROM image_names, image_features ' \
        f'WHERE `image_names`.`id`={image_id} AND `image_features`.`image_id`={image_id}'

    cursor = connection.cursor()
    cursor.execute(statement)
    result = cursor.fetchone()
    cursor.close()
    return result[0], result[1], numpy.array(json.loads(result[2]))
