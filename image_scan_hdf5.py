import argparse
import logging
import os

import h5py

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

valid_image_files = [
    ".jpg", '.jpeg', '.png'
]


def create_image_path_list(root_directory):
    data = []
    logger.info(f'Collecting JPEGs in directory "{root_directory}".')
    for root, dirs, files in os.walk(root_directory):
        for file in files:
            for valid_image_file_suffix in valid_image_files:
                if file.lower().endswith(valid_image_file_suffix):
                    data.append((file, os.path.abspath(f'{root}/{file}')))
                    break
    logger.info(f'{len(data)} images found.')

    return data


if __name__ == "__main__":
    options = vars(parser.parse_args())
    image_path_list = create_image_path_list(options['source'])

    f = h5py.File(f"{options['project']}.hdf5", "w")

    for image_path in image_path_list:
        g = f.create_group(image_path[0])
        g.attrs['path'] = image_path[1]

    f.close()
