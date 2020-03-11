import argparse
import logging
import os

import image_scan_hdf5
import feature_creation_hdf5
import create_neighbours_hdf5

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


parser = argparse.ArgumentParser(description="Scan for images in the source directory.")
parser.add_argument('project', type=str, help="Specifiy project name.")
parser.add_argument('source', type=is_readable_directory, help="specify input directory.")
parser.add_argument('-k', '--k_nearest', type=int, default=20,
                    help="keep k nearest neighbours for each image image, default: 20")

valid_image_files = [
    ".jpg", '.jpeg', '.png'
]


if __name__ == "__main__":
    options = vars(parser.parse_args())

    image_scan_hdf5.start(options['source'], options['project'])
    feature_creation_hdf5.create_features(options['project'])
    create_neighbours_hdf5.create_neighbours(options['project'], options['k_nearest'])

