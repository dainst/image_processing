import sys
import os
import pickle

import tensorflow as tf
import numpy as np


def create_graph():
    with tf.gfile.FastGFile('./model/classify_image_graph_def.pb', 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        _ = tf.import_graph_def(graph_def, name='')


def create_features(image_list):

    create_graph()

    result = []

    with tf.Session() as sess:

        for image_idx, image in enumerate(image_list):
            try:
                print(f"Parsing {image}, (#{image_idx})...")
                if not tf.gfile.Exists(image):
                    tf.logging.fatal(f'File does not exist {image}.')

                with tf.gfile.FastGFile(image, 'rb') as f:
                    image_data = f.read()

                    feature_tensor = sess.graph.get_tensor_by_name('pool_3:0')
                    feature_set = sess.run(feature_tensor, {'DecodeJpeg/contents:0': image_data})
                    feature_vector = np.squeeze(feature_set)

                    print(feature_vector.shape)

                    result.append((os.path.basename(image), feature_vector))

            except Exception as e:
                print(e)

    return result


if __name__ == '__main__':
    image_root = sys.argv[1]

    file_list = []

    for root, dirs, files in os.walk(image_root):
        for file in files:
            if file.endswith('.jpg'):
                file_list.append(os.path.abspath(f"{root}/{file}"))

    features = create_features(image_list=file_list)

    with open(sys.argv[2] + '/features.pickle', 'wb') as file:
        pickle.dump(features, file)

    print('Done.')
