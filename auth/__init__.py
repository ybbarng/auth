import os

from dotenv import load_dotenv
from flask import Flask, url_for
from flask_dance.contrib.slack import make_slack_blueprint
from werkzeug.contrib.fixers import ProxyFix

from auth.routes import routes
from auth.middleware import PrefixMiddleware


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    load_dotenv()

    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix='/auth')
    app.secret_key = bytes.fromhex(os.getenv('FLASK_SECRET_KEY_HEX'))
    CLIENT_ID = os.getenv('SLACK_CREDENTIAL_CLIENT_ID')
    CLIENT_SECRET = os.getenv('SLACK_CREDENTIAL_CLIENT_SECRET')

    login_blueprint = make_slack_blueprint(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scope=['identity.basic,identity.team'],
        redirect_url='/auth'
    )
    app.register_blueprint(login_blueprint, url_prefix='/login')
    app.register_blueprint(routes)
    return app
