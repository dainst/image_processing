import h5py

import argparse
import logging
import os
import pickle

import numpy
from datetime import datetime


import keras

from keras.layers import Dense
from keras.models import Sequential, Model, load_model
from keras.optimizers import Adadelta

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
parser.add_argument('project', type=str, help="Specifiy project name.")


def euclidean_distance_loss(y_true, y_pred):
    """
    Euclidean distance loss
    https://en.wikipedia.org/wiki/Euclidean_distance
    :param y_true: TensorFlow/Theano tensor
    :param y_pred: TensorFlow/Theano tensor of the same shape as y_true
    :return: float
    """
    return keras.backend.sqrt(keras.backend.sum(keras.backend.square(y_pred - y_true), axis=-1))


def train_autoencoder(training_features, test_features, project_name):

    logger.info("Training autoencoder...")

    # Stop if there has been no improvement for 100 epochs
    es = keras.callbacks.EarlyStopping(verbose=1, patience=100)
    # Save best model while training
    mc = keras.callbacks.ModelCheckpoint(f'model/{project_name}_best_model.hdf5')

    callbacks_list = [es, mc]

    m = Sequential()

    m.add(Dense(512, activation='elu', input_shape=(training_features.shape[1],)))
    m.add(Dense(256, activation='elu'))
    m.add(Dense(32, activation='linear', name="bottleneck"))
    m.add(Dense(256, activation='elu'))
    m.add(Dense(512, activation='elu'))
    m.add(Dense(training_features.shape[1], activation='sigmoid'))

    m.compile(loss=euclidean_distance_loss, optimizer=Adadelta())

    history = m.fit(training_features, training_features, batch_size=128, epochs=100000, verbose=1,
                    validation_data=(test_features, test_features), callbacks=callbacks_list)

    with open(f'model/{project_name}_autoencoder_training_history_' + datetime.today().strftime('%Y-%m-%d'), 'wb') as history_file:
        pickle.dump(history.history, history_file)

    logger.info("Loading best model encountered while training.")
    best_model = load_model(f'model/{project_name}_best_model.hdf5',
                            custom_objects={
                                'euclidean_distance_loss': euclidean_distance_loss}
                            )
    logger.info("Slicing best model up to center layer, resulting in encoder (omitting decoder).")
    encoder = Model(best_model.input, best_model.get_layer('bottleneck').output)

    logger.info("Loading original ResNet50 model.")
    res_net = keras.applications.resnet50.ResNet50(include_top=False, pooling='avg')

    logger.info("Combining models ResNet50 and sliced encoder model")
    combined = Model(inputs=res_net.input, outputs=encoder(res_net.output))
    combined.save(f'model/{project_name}_encoder.hdf5')
    logger.info("  Done.")


def start(project_name):
    f = h5py.File(f'./projects/{project_name}.hdf5', 'r+')

    counter = 0

    training_data = []
    test_data = []
    for key in f:
        if counter % 5 == 0:
            test_data += [f[key]['features'][()]]
        else:
            training_data += [f[key]['features'][()]]
        counter += 1

    training_data = numpy.array(training_data)
    test_data = numpy.array(test_data)

    train_autoencoder(training_data, test_data, project_name)


if __name__ == "__main__":
    options = vars(parser.parse_args())

    start(options['project'])
