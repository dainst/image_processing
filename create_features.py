import h5py

import argparse
import logging
import json

import keras
import numpy as np
import os

from keras.preprocessing import image
from keras.applications.resnet50 import preprocess_input
from PIL.Image import DecompressionBombError
from typing import Tuple, Callable

from global_directories import GloabalDir


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.basicConfig(format="%(asctime)s-%(levelname)s-%(name)s - %(message)s")

parser = argparse.ArgumentParser(description="Scan for images in the source directory.")
parser.add_argument('project', type=str, help="Specifiy project name.")


def create_features(project_name: str) -> None:
    logger.info("Loading models...")
    res_net = keras.applications.resnet50.ResNet50(include_top=False, pooling='avg')

    f = h5py.File(f'{os.path.join(GloabalDir.projects,project_name)}.hdf5', 'r+')

    with open(f"{os.path.join(GloabalDir.projects,project_name)}.info", "r") as info:
        absolute_path = json.loads(info.read())['initial_absolute_path']

    key_count = len(f.keys())
    for counter, key in enumerate(f, start=1):
        g = f[key]
        image_path = f"{absolute_path}/{g.attrs['path']}"
        try:
            if counter % 100 == 0:
                logger.info(f'Progress: {counter}/{key_count}')

            res_net_feature_flattened = create_image_feature_vector(image_path, res_net, preprocess_input)
            features = g.create_dataset("features", data=res_net_feature_flattened)
            features.attrs['model'] = "keras.applications.resnet50.ResNet50"

            counter += 1

        except OSError as e:
            logger.error(e)
            logger.error(f"Removing {key} from hdf5 dataset.")
            del f[key]
        except DecompressionBombError as e:
            logger.error(e)
            logger.error(image_path)
            logger.error(f"Removing {key} from hdf5 dataset.")
            del f[key]

    logger.info(f'Done')
    f.close()

def create_image_feature_vector(image_path: str, model: keras.Model, preporcess_function: Callable, target_size: Tuple[int, int] = (244,244)) -> np.ndarray:
    """ Reads image and returns flattened feature vector of given image """
    img = image.load_img(image_path, target_size=target_size)
    img_data = image.img_to_array(img)
    img_data = np.expand_dims(img_data, axis=0)
    img_data = preporcess_function(img_data)

    model_feature = model.predict(img_data)
    return np.array(model_feature).flatten()

if __name__ == "__main__":
    create_features(vars(parser.parse_args()))
