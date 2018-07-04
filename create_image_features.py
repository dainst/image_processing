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


def create_features(image_list):

    result_name_mapping = []
    result_features = []

    with tf.Session() as sess:
        for image_idx, image in enumerate(image_list):
            try:
                logger.debug(f"Parsing {image}, (#{image_idx})...")
                if not tf.gfile.Exists(image):
                    tf.logging.fatal(f'File does not exist {image}.')

                with tf.gfile.FastGFile(image, 'rb') as f:
                    image_data = f.read()

                    feature_tensor = sess.graph.get_tensor_by_name('pool_3:0')
                    feature_set = sess.run(feature_tensor, {'DecodeJpeg/contents:0': image_data})
                    feature_vector = np.squeeze(feature_set)

                    result_name_mapping.append(os.path.basename(image))
                    current_index = len(result_name_mapping) - 1
                    result_features.append(np.append([current_index], feature_vector))

            except Exception as e:
                logger.error(e)
                logger.error(image)

    return result_name_mapping, np.array(result_features)


def process_file_list(path_list):
    result_name_mapping = []
    result_features = []

    with tf.Session() as sess:
        for image_idx, image in enumerate(path_list):
            try:
                logger.debug(f"Parsing {image}, (#{image_idx})...")
                if not tf.gfile.Exists(image):
                    tf.logging.fatal(f'File does not exist {image}.')

                with tf.gfile.FastGFile(image, 'rb') as f:
                    image_data = f.read()

                    feature_tensor = sess.graph.get_tensor_by_name('pool_3:0')
                    feature_set = sess.run(feature_tensor, {'DecodeJpeg/contents:0': image_data})
                    feature_vector = np.squeeze(feature_set)

                    mariadb.write_file_features(os.path.basename(image), feature_vector)

            except Exception as e:
                logger.error(e)
                logger.error(image)

    return result_name_mapping, np.array(result_features)


if __name__ == '__main__':
    image_root = sys.argv[1]
    output_root = sys.argv[2]

    mariadb.establish_connection()

    if not output_root.endswith('/'):
        output_root += '/'

    path_list = []
    file_list = []

    image_counter = 0
    batch_counter = 0

    logger.info('Creating graph.')
    create_graph()

    logger.info('Starting to process images...')
    for root, dirs, files in os.walk(image_root):
        for file in files:
            if file.endswith('.jpg'):
                path_list.append(os.path.abspath(f"{root}/{file}"))
                file_list.append(file)

    mariadb.write_filename(file_list=file_list)
    process_file_list(path_list)

    logger.info('Done.')
