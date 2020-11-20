import argparse
import logging
import os
import json
import h5py
from typing import List, Tuple

import create_features
import create_neighbours
from global_directories import GloabalDir

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
parser.add_argument('-k', '--k_nearest', type=str, default='all',
                    help="keep k nearest neighbours for each image image, default: all. If given value is all: All images from dataset are compared")

valid_image_files = [
    ".jpg", '.jpeg', '.png'
]


def create_image_path_list(root_directory: str) -> List[Tuple[str, str]]:
    data = []

    if root_directory[-1] != '/':
        root_directory += "/"

    logger.info(f'Collecting JPEGs in directory "{root_directory}".')
    for root, _, files in os.walk(root_directory):
        for file in files:
            for valid_image_file_suffix in valid_image_files:
                if file.lower().endswith(valid_image_file_suffix):
                    relative_path = f"{root.replace(root_directory, '')}/{file}"
                    data += [(file, relative_path)]
                    break

    logger.info(f'{len(data)} images found.')

    return data


def scan_for_images(source_directory: str, project_name: str) -> None:

    image_path_list = create_image_path_list(source_directory)
    with open(f"{os.path.join(GloabalDir.projects,project_name)}.info", "w") as info:
        data = {
            "initial_absolute_path": os.path.abspath(source_directory)
        }
        info.write(json.dumps(data))

    f = h5py.File(f"{os.path.join(GloabalDir.projects,project_name)}.hdf5", "w")

    for image_path in image_path_list:
        file, relative_path = image_path
        g = f.create_group(file)
        g.attrs['path'] = relative_path

    f.close()


if __name__ == "__main__":
    options = vars(parser.parse_args())

    scan_for_images(options['source'], options['project'])
    create_features.create_features(options['project'])
    create_neighbours.create_neighbours(options['project'], options['k_nearest'])

