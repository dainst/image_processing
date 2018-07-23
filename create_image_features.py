import sys
import os
import logging
import db.mariadb as mariadb

import tensorflow as tf
import numpy as np

logging.basicConfig(format='%(asctime)s-%(levelname)s-%(name)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def create_graph():
    with tf.gfile.FastGFile('./model/classify_image_graph_def.pb', 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        _ = tf.import_graph_def(graph_def, name='')


def already_processed(file_path, connection):
    file_name = os.path.basename(file_path)
    result = mariadb.get_features_by_name(file_name, connection)
    return result is not None


def process_file_list(path_list, connection):

    with tf.Session() as sess:
        for image_idx, image in enumerate(path_list):
            try:
                if image_idx % 1000 == 0:
                    logger.info(f'Processed {image_idx} of {len(path_list)}.')

                # Already processed images (= images with an associated feature-vector) are skipped
                if already_processed(image, connection):
                    continue

                logger.debug(f'Parsing {image}, (#{image_idx})...')
                if not tf.gfile.Exists(image):
                    tf.logging.fatal(f'File does not exist {image}.')

                with tf.gfile.FastGFile(image, 'rb') as f:
                    image_data = f.read()

                    feature_tensor = sess.graph.get_tensor_by_name('pool_3:0')
                    feature_set = sess.run(feature_tensor, {'DecodeJpeg/contents:0': image_data})
                    feature_vector = np.squeeze(feature_set)

                    mariadb.write_file_features(os.path.basename(image), feature_vector, connection)

            except Exception as e:
                logger.error(e)
                logger.error(image)


if __name__ == '__main__':

    if len(sys.argv) != 7:
        logger.info('Please provide as arguments: ')
        logger.info(' 1) Path to image root directory.')
        logger.info(' 2) MariaDB host.')
        logger.info(' 3) MariaDB port.')
        logger.info(' 4) MariaDB database name.')
        logger.info(' 5) MariaDB user.')
        logger.info(' 6) MariaDB password.')
        sys.exit()

    image_root = sys.argv[1]

    connection = mariadb.get_connection(
        host=sys.argv[2],
        port=int(sys.argv[3]),
        db_name=sys.argv[4],
        user=sys.argv[5],
        password=sys.argv[6]
    )

    path_list = []
    file_list = []

    image_counter = 0
    batch_counter = 0

    logger.info('Creating graph.')
    create_graph()

    logger.info(f'Collecting JPEGs in directory {image_root}.')
    for root, dirs, files in os.walk(image_root):
        for file in files:
            if file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.JPG') or file.endswith('JPEG'):
                path_list.append(os.path.abspath(f'{root}/{file}'))
                file_list.append(file)

    logger.info('Writing file names to database.')
    mariadb.write_file_names(file_list=file_list, connection=connection)

    logger.info('Starting to process images...')
    process_file_list(path_list, connection)
    logger.info('Done.')

    connection.close()
