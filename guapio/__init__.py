import os

from flask import Flask, url_for

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        DEBUG=True,
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'database.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from guapio import db
    db.init_app(app)

    # apply the blueprints to the app
    from guapio import auth, blog, currency, balance, user_move

    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)
    app.register_blueprint(currency.bp)
    app.register_blueprint(balance.bp)
    app.register_blueprint(user_move.bp)
    # app.register_blueprint(routes.bp)

    # with app.test_request_context():
    #     print(url_for('static', filename='style.css'))
    #     print(url_for('hello'))
    #     print(url_for('auth.login'))
    #     print(url_for('auth.login', next='/'))
    #     print(url_for('routes.profile', username='John Doe'))
    app.add_url_rule('/', endpoint='index')

    return app
