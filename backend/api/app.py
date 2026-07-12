#test

from config import Config
from flask_cors import CORS
from apifairy import APIFairy
from alchemical.flask import Alchemical
from flask_marshmallow import Marshmallow
from flask import Flask, redirect, url_for


cors = CORS()
db = Alchemical()
ma = Marshmallow()
apifairy = APIFairy()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Extensions
    db.init_app(app)
    ma.init_app(app)
    cors.init_app(app)
    apifairy.init_app(app)

    # Blueprints
    from api.errors import errors
    app.register_blueprint(errors)

    from api.radios import radios
    app.register_blueprint(radios, url_prefix='/api')

    from api.artists import artists
    app.register_blueprint(artists, url_prefix='/api')

    from api.songs import songs
    app.register_blueprint(songs, url_prefix='/api')

    from api.plays import plays
    app.register_blueprint(plays, url_prefix='/api')

    from api.no_mcrs import no_mcrs
    app.register_blueprint(no_mcrs, url_prefix='/api')

    @app.route('/')
    def index():
        return redirect(url_for('apifairy.docs'))

    return app
