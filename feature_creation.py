# RUN AUTOENCODER JUPYTER NOTEBOOK FIRST, this will create the `encoder.h5` file used below

import argparse
import logging
import keras
import numpy as np

from keras.models import load_model, Model
from keras.preprocessing import image
from keras.applications.resnet50 import preprocess_input
import keras.backend as K
from PIL.Image import DecompressionBombError

import db.mariadb as mariadb

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.basicConfig(format="%(asctime)s-%(levelname)s-%(name)s - %(message)s")

parser = argparse.ArgumentParser(description="Create features for files in MariaDB.")
parser.add_argument('model_path', help="path to keras model.")
parser.add_argument('db_host', help="specify mariadb host.")
parser.add_argument('db_port', type=int, help="specify mariadb port.")
parser.add_argument('db_name', help="specify mariadb database.")
parser.add_argument('db_user', help="specify mariadb user.")
parser.add_argument('db_password', help="specify mariadb password.")


def create_features(model_path, host, port, database, user, password):
    logger.info("Loading models...")
    res_net = keras.applications.resnet50.ResNet50(include_top=False, pooling='avg')

    encoder = load_model(model_path)

    logger.info("Combining models...")
    combined = Model(inputs=res_net.input, outputs=encoder(res_net.output))

    con = mariadb.get_connection(host, port, database, user, password)

    files_batch = mariadb.get_all_files_data(con)

    # Create training and test features
    logger.info("Creating image features using both models.")
    counter = 1

    for (img_id, name, path, url) in files_batch:
        try:
            if counter % 100 == 0:
                logger.info(f'Progress: {counter}/{len(files_batch)}')

            img = image.load_img(path, target_size=(224, 224))
            img_data = image.img_to_array(img)
            img_data = np.expand_dims(img_data, axis=0)
            img_data = preprocess_input(img_data)

            combined_feature = combined.predict(img_data)
            combined_feature = np.array(combined_feature).flatten()

            res_net_feature = res_net.predict(img_data)
            res_net_feature = np.array(res_net_feature).flatten()

            mariadb.write_file_features(img_id, combined_feature, con)
            mariadb.write_uncompressed_file_features(img_id, res_net_feature, con)

            counter += 1

        except OSError as e:
            logger.error(e)
        except DecompressionBombError as e:
            logger.error(e)
            logger.error(path)

    con.close()
    logger.info('Done.')


if __name__ == "__main__":
    options = vars(parser.parse_args())

    create_features(options['model_path'], options['db_host'], options['db_port'], options['db_name'],
                    options['db_user'], options['db_password'])
