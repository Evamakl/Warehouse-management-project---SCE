"""
Website Package
===============

This package contains the Flask application for the website.

Modules:
- routes: Contains the route definitions and view functions.

"""
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

DATDBASE_NAME = "database.db"
app = Flask(__name__)
#app.config['SECRET_KEY'] -> encrypt the cookies and session data
app.config['SECRET_KEY'] = '60cd05d35cd3e4c34c6e4b45'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATDBASE_NAME


#for unit test:---------------------------
#if you want to run the unit test run this row, else put in remarks
#app.config['SERVER_NAME'] = 'localhost'
#-----------------------------------------

app.app_context().push()
db = SQLAlchemy(app)

#Bcrypt -> password hashing function that is used to store user passwords securely in databases.
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
from . import routes





def create_app():
    """
    Creates and configures the Flask application.

    Returns:
        The configured Flask application.
    """
    # Register the routes
    from .routes import bp
    app.register_blueprint(bp)

    return app
