from flask import Flask, jsonify, request, url_for
from flask_cors import CORS
import db.mariadb as mariadb

app = Flask('nlp_service')
cors = CORS(app, resources={r'*': {'origins': 'http://localhost*'}})
app.debug = True

mariadb.establish_connection('127.0.0.1', 'main_user', 'pwd', 3308)


@app.route('/')
def index():
    app.logger.debug('Hello Wolfgang! Says the debug logger...')
    return 'Hello Wolfgang!'


@app.route('/image/<image_id>', methods=['GET'])
def image(image_id):
    app.logger.debug(f'Image  requested.')
    query_result = mariadb.get_image_and_neigbours_by_id(image_id)

    return jsonify(query_result)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
