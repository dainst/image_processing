import logging
import MySQLdb
import json

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


def commit():
    global connection

