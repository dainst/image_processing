import sys
import os
import pickle
import json
import logging

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

    return result_name_mapping, result_features


def process_file_list(image_list, path, batch_count):
    logger.debug(len(image_list))

    (name_list, features) = create_features(image_list=image_list)
    batch_path = f'{path}{batch_count}/'

    logger.info(f"Writing processed batch {batch_count}.")

    if not os.path.exists(os.path.dirname(batch_path)):
        os.makedirs(os.path.dirname(batch_path))

    with open(batch_path + '/features.pickle', 'wb') as output_file:
        pickle.dump(features, output_file)

    with open(batch_path + '/image_mapping.json', 'w') as output_file:
        json.dump(name_list, output_file)


if __name__ == '__main__':
    image_root = sys.argv[1]
    output_root = sys.argv[2]

    if not output_root.endswith('/'):
        output_root += '/'

    file_list = []

    image_counter = 0
    batch_counter = 0

    logger.info('Creating graph.')
    create_graph()

    logger.info('Starting to process images...')
    for root, dirs, files in os.walk(image_root):
        for file in files:
            if file.endswith('.jpg'):
                file_list.append(os.path.abspath(f"{root}/{file}"))
                image_counter += 1

            if image_counter == 10000:
                process_file_list(file_list, output_root, batch_counter)
                batch_counter += 1
                image_counter = 0
                file_list = []

    if len(file_list) != 0:
        process_file_list(file_list, output_root, batch_counter)

    logger.info('Done.')
