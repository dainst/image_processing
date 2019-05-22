import argparse
import logging
import os
import json

import db.mariadb as mariadb
import MySQLdb._exceptions as mysql_exceptions
from requests_futures.sessions import FuturesSession
from random import shuffle

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
parser.add_argument('source', type=is_readable_directory, help="specify input directory.")
parser.add_argument('db_host', help="specify mariadb host.")
parser.add_argument('db_port', type=int, help="specify mariadb port.")
parser.add_argument('db_name', help="specify mariadb database.")
parser.add_argument('db_user', help="specify mariadb user.")
parser.add_argument('db_password', help="specify mariadb password.")
parser.add_argument('-n', '--nth_image', type=int, default=1,
                    help="only keep every nth image found in source directory, default: 1 (every image)")


def create_image_path_list(root_directory):
    data = []
    logger.info(f'Collecting JPEGs in directory "{root_directory}".')
    for root, dirs, files in os.walk(root_directory):
        for file in files:
            if file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.JPG') or file.endswith('JPEG'):
                data.append((file, os.path.abspath(f'{root}/{file}'), None))

    logger.info(f'{len(data)} images found.')

    return data


def process_image_list(image_paths, host, port, database, user, password):

    batch_counter = 0
    batch_size = 1000

    logger.info('Processing batches.')
    logger.info('  Trying to resolve Arachne URLs, this may take some time.')

    while batch_counter < len(image_paths):

        logger.info(f"  Processing batch {batch_counter} to {batch_counter+batch_size} of {len(image_paths)}.")
        current_batch = image_paths[batch_counter:batch_counter+batch_size]

        session = FuturesSession(max_workers=10)

        arachne_path = 'https://arachne.dainst.org/data'
        futures = []

        for (name, _path, _url) in current_batch:
            futures.append(session.get(f'{arachne_path}/search?q={name}'))

        for idx, response in enumerate(futures):

            try:
                entity_id = None
                json_value = response.result().json()
                if json_value['size'] == 1:
                    entity_id = json_value['entities'][0]['entityId']

                if entity_id is not None:
                    current_batch[idx] = (current_batch[idx][0], current_batch[idx][1],
                                          f'{arachne_path}/image/{entity_id}')
            except json.decoder.JSONDecodeError as e:
                logger.error(e)
                logger.error(response)

        con = mariadb.get_connection(host, port, database, user, password)
        try:
            mariadb.write_files_data(current_batch, con)
        except mysql_exceptions.DataError as e:
            logger.error(e)
        con.close()

        batch_counter += batch_size

    logger.info('Done.')


if __name__ == "__main__":
    options = vars(parser.parse_args())
    image_path_list = create_image_path_list(options['source'])

    shuffle(image_path_list)

    image_path_list = image_path_list[::options['nth_image']]
    logger.info(f'{len(image_path_list)} images are used.')

    process_image_list(image_path_list, options['db_host'], options['db_port'], options['db_name'], options['db_user'],
                       options['db_password'])
