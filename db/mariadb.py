import logging
import MySQLdb
import json
import numpy

logging.basicConfig(format='%(asctime)s-%(levelname)s-%(name)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

connection = None


def get_db_name():
    return 'image_processing_db'


def get_cursor():
    global connection

    return connection.cursor()


def establish_connection():
    global connection

    connection = MySQLdb.connect(host="127.0.0.1", user="main_user", passwd="pwd", db=get_db_name(), port=3308,
                                 use_unicode=True, charset='utf8')


def write_filename(file_list):
    global connection

    statement = 'INSERT IGNORE INTO `image_names` (`file_name`) VALUES\n'
    for idx, image_name in enumerate(file_list):
        statement += f'("{image_name}"),\n'

    statement = statement[0:-2]

    cursor = connection.cursor()
    cursor.execute(statement)
    connection.commit()
    cursor.close()


def write_file_features(file_name, features):
    global connection
    statement = 'INSERT IGNORE INTO `image_features` (`image_id`, `features`) ' \
                'VALUES ((SELECT `id` FROM `image_names` WHERE `file_name` = "' + file_name + '"), "' + json.dumps(features.tolist()) +'");'

    cursor = connection.cursor()
    cursor.execute(statement)
    connection.commit()
    cursor.close()


def get_feature_count():
    global connection
    statement = 'SELECT count(*) FROM `image_features`;'

    cursor = connection.cursor()
    cursor.execute(statement)
    result = cursor.fetchone()

    return result[0]


def _get_feature_batch_data(offset, size):
    global connection
    statement = 'SELECT * FROM `image_features` WHERE `image_id` >= ' + str(offset) + ' AND `image_id` < ' + str(offset + size) + ';'

    cursor = connection.cursor()
    cursor.execute(statement)

    result = cursor.fetchall()

    return result


def get_feature_batch(offset, batch_size):
    batch_data = _get_feature_batch_data(offset, batch_size)
    batch_feature_vectors = []
    batch_feature_ids = []
    for (image_id, feature_string) in batch_data:
        batch_feature_vectors.append(json.loads(feature_string))
        batch_feature_ids.append(image_id)

    matrix = numpy.array(batch_feature_vectors)

    return batch_feature_ids, matrix


def write_neighbours(image_id, neighbours):
    global connection
    statement = 'INSERT IGNORE INTO `image_neighbours` (`image_id`, `neighbours`) ' \
                'VALUES (' + str(image_id) + ', "' + json.dumps(neighbours) + '");'

    cursor = connection.cursor()
    cursor.execute(statement)
    connection.commit()
    cursor.close()


def commit():
    global connection

