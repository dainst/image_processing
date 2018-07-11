
from flask import Flask, jsonify, request, url_for
from flask_cors import CORS

app = Flask('nlp_service')
cors = CORS(app, resources={r"*": {"origins": "http://localhost*"}})
app.debug = True


@app.route('/')
def index():
    app.logger.debug('Hello Wolfgang! Says the debug logger...')
    return 'Hello Wolfgang!'


if __name__ == '__main__':
    app.run(host='0.0.0.0')
