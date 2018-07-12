import sys
import os
import logging

logging.basicConfig(format='%(asctime)s-%(levelname)s-%(name)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


if __name__ == '__main__':

    if len(sys.argv) != 2:
        logger.info('Please provide as arguments: ')
        logger.info(' 1) Path to image root directory.')

    image_root = sys.argv[1]

    known_images = {}

    logger.info('Starting to process images...')
    for root, dirs, files in os.walk(image_root):
        for file in files:
            if file.endswith('.jpg'):
                if file in known_images:
                    logger.error(file)
                    known_images[file] += [os.path.abspath(f'{root}/{file}')]
                else:
                    known_images[file] = [os.path.abspath(f'{root}/{file}')]

    for file in known_images:
        if len(known_images[file]) != 1:
            logger.info(f'{len(known_images[file])} duplicates for file name {file}:')
            for path in known_images[file]:
                logger.info(f'  {path}')

    logger.info('Done.')
