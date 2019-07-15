import os
from flask import Flask
from flask_cors import CORS

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev'
        )

    CORS(app)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)


    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    from . import parser
    app.register_blueprint(parser.bp)
    app.add_url_rule('/pa-deficits', endpoint='upload_file')
    app.add_url_rule('/pa-deficits/<filename>', endpoint='download_file')
    app.add_url_rule('/login', endpoint='user_login')

    return app
