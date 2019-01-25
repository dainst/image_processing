import argparse
import logging
import db.mariadb as mariadb
import os

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


def scan(image_directory, connection, resolve_arachne_url):

    data = []

    logger.info(f'Collecting JPEGs in directory {image_directory}.')
    for root, dirs, files in os.walk(image_directory):
        for file in files:
            if file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.JPG') or file.endswith('JPEG'):
                data.append((file, os.path.abspath(f'{root}/{file}'), None))

    if resolve_arachne_url:
        logger.info('Trying to resolve Arachne URLs, this may take some time.')

        session = FuturesSession(max_workers=100)

        arachne_path = 'https://arachne.dainst.org/data'
        futures = []
        for (name, _path, _url) in data:
            futures.append(session.get(f'{arachne_path}/search?q={name}'))

        for idx, response in enumerate(futures):
            entity_id = None
            json_value = response.result().json()
            if json_value['size'] == 1:
                entity_id = json_value['entities'][0]['entityId']
            data[idx] = (data[idx][0], data[idx][1], f'{arachne_path}/image/{entity_id}')

    logger.info('Writing file data to database..')
    mariadb.write_files_data(data, connection)


if __name__ == '__main__':
    args = parser.parse_args()

    con = mariadb.get_connection(args.host, int(args.port), args.db, args.user, args.password)
    scan(args.dir, con, args.arachne is True)
    con.close()
