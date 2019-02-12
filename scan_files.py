import argparse
import logging
import db.mariadb as mariadb
import os
import json

from requests_futures.sessions import FuturesSession

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.basicConfig(format='%(asctime)s-%(levelname)s-%(name)s - %(message)s')

parser = argparse.ArgumentParser(description='Scans a given directory and all its subdirectories for images. '
                                             'Writes image names and paths to MariaDB.')

parser.add_argument("dir", help="Directory to recursively search for images.")
parser.add_argument("host", help="MariaDB host.")
parser.add_argument("port", help="MariaDB port.")
parser.add_argument("db", help="MariaDB database.")
parser.add_argument("user", help="MariaDB user.")
parser.add_argument("password", help="MariaDB user password")
parser.add_argument("--arachne", help="Try retrieving Arachne URLs for image names (https://arachne.dainst.org)",
                    action="store_true")


def scan(image_directory, db_host, db_port, db_name, db_user, db_password , resolve_arachne_url):

    data = []

    logger.info(f'Collecting JPEGs in directory {image_directory}.')
    for root, dirs, files in os.walk(image_directory):
        for file in files:
            if file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.JPG') or file.endswith('JPEG'):
                data.append((file, os.path.abspath(f'{root}/{file}'), None))

    batch_counter = 0
    batch_size = 1000

    logger.info('Processing batches.')
    if resolve_arachne_url:
        logger.info('  Trying to resolve Arachne URLs, this may take some time.')

    while batch_counter < len(data):

        logger.info(f"  Processing batch {batch_counter} to {batch_counter+batch_size} of {len(data)}.")
        current_batch = data[batch_counter:batch_counter+batch_size]

        if resolve_arachne_url:

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
                    current_batch[idx] = (current_batch[idx][0], current_batch[idx][1],
                                          f'{arachne_path}/image/{entity_id}')
                except json.decoder.JSONDecodeError as e:
                    logger.error(e)
                    logger.error(response)

        con = mariadb.get_connection(db_host, db_port, db_name, db_user, db_password)
        mariadb.write_files_data(current_batch, con)
        con.close()

        batch_counter += batch_size


if __name__ == '__main__':
    args = parser.parse_args()
    scan(args.dir, args.host, int(args.port), args.db, args.user, args.password, args.arachne is True)
