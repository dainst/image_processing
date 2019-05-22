import argparse
import logging
import os
import pickle
import numpy as np
from datetime import datetime


import keras

from keras.applications.resnet50 import preprocess_input
from keras.layers import Dense
from keras.models import Sequential, Model, load_model
from keras.optimizers import Adadelta
from keras.preprocessing import image
from PIL.Image import DecompressionBombError

import db.mariadb as mariadb

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.basicConfig(format="%(asctime)s-%(levelname)s-%(name)s - %(message)s")


def is_readable_directory(path: str):
    directory = os.path.dirname(path)
    if not os.path.isdir(directory) or not os.access(directory, os.R_OK):
        msg = f"Please provide readable directory."
        raise argparse.ArgumentTypeError(msg)
    else:
        return path


parser = argparse.ArgumentParser(description="Train encoder based on images indexed in MariaDB.")
parser.add_argument('db_host', help="specify mariadb host.")
parser.add_argument('db_port', type=int, help="specify mariadb port.")
parser.add_argument('db_name', help="specify mariadb database.")
parser.add_argument('db_user', help="specify mariadb user.")
parser.add_argument('db_password', help="specify mariadb password.")
parser.add_argument('-n', '--nth_image', type=int, default=1,
                    help="only keep every nth image found in source directory, default: 1 (every image)")

# Initialize and run autoencoder


def euclidean_distance_loss(y_true, y_pred):
    """
    Euclidean distance loss
    https://en.wikipedia.org/wiki/Euclidean_distance
    :param y_true: TensorFlow/Theano tensor
    :param y_pred: TensorFlow/Theano tensor of the same shape as y_true
    :return: float
    """
    return keras.backend.sqrt(keras.backend.sum(keras.backend.square(y_pred - y_true), axis=-1))


def create_features(image_list):
    features_train = []
    features_test = []

    logger.info("Creating features...")

    model = keras.applications.resnet50.ResNet50(include_top=False, pooling='avg')

    # Create training and test features
    counter = 1
    for path in image_list:
        try:
            img = keras.preprocessing.image.load_img(path, target_size=(224, 224))

            img_data = image.img_to_array(img)
            img_data = np.expand_dims(img_data, axis=0)
            img_data = preprocess_input(img_data)

            res_net_feature = model.predict(img_data)
            res_net_feature = np.array(res_net_feature).flatten()

            if counter % 3 == 0:
                features_test.append(res_net_feature)
            else:
                features_train.append(res_net_feature)

            counter += 1

        except OSError as e:
            logger.error(e)
        except DecompressionBombError as e:
            logger.error(e)
            logger.error(path)

    features_train = np.array(features_train)
    features_test = np.array(features_test)

    # We need to scale the features to values between 0 and 1, because the sigmoid layer (last autoencoder layer)
    # produces values in that range. Without scaling the original values down, the autoencoder won't be able to
    # reproduce input values > 1.

    if np.max(features_train) > np.max(features_test):
        features_train_scaled = features_train / np.max(features_train)
        features_test_scaled = features_test / np.max(features_train)
    else:
        features_train_scaled = features_train / np.max(features_test)
        features_test_scaled = features_test / np.max(features_test)

    logger.info("  Done.")

    return features_train_scaled, features_test_scaled


def train_autoencoder(training_features, test_features):

    logger.info("Training autoencoder...")

    # Stop if there has been no improvement for 100 epochs
    es = keras.callbacks.EarlyStopping(verbose=1, patience=100)
    # Save best model while training
    mc = keras.callbacks.ModelCheckpoint('model/best_model.h5')

    callbacks_list = [es, mc]

    m = Sequential()

    m.add(Dense(512, activation='elu', input_shape=(training_features.shape[1],)))
    m.add(Dense(32, activation='linear', name="bottleneck"))
    m.add(Dense(512, activation='elu'))
    m.add(Dense(training_features.shape[1], activation='sigmoid'))

    m.compile(loss=euclidean_distance_loss, optimizer=Adadelta())

    history = m.fit(training_features, training_features, batch_size=128, epochs=100000, verbose=1,
                    validation_data=(test_features, test_features), callbacks=callbacks_list)

    with open('model/autoencoder_training_history_' + datetime.today().strftime('%Y-%m-%d'), 'wb') as history_file:
        pickle.dump(history.history, history_file)

    best_model = load_model('model/best_model.h5', custom_objects={'euclidean_distance_loss': euclidean_distance_loss})
    encoder = Model(best_model.input, best_model.get_layer('bottleneck').output)
    encoder.save('model/encoder.h5')

    logger.info("  Done.")


def start(host, port, database, user, password, n):
    con = mariadb.get_connection(host, port, database, user, password)
    files_paths = [i[0] for i in mariadb.get_all_file_paths(con)]
    con.close()

    logger.info(f"File paths in database: {len(files_paths)}")
    files_paths = files_paths[::n]
    logger.info(f"  using: {len(files_paths)}.")

    (training_features, test_features) = create_features(files_paths)
    train_autoencoder(training_features, test_features)


if __name__ == "__main__":
    options = vars(parser.parse_args())

    start(options['db_host'], options['db_port'], options['db_name'], options['db_user'],
          options['db_password'], options['nth_image'])
