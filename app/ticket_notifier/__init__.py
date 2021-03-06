import os
import boto3
import logging
import threading
import requests
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from app.instance.config import app_config


POOL_TIME = 5  # Seconds
# variables that are accessible from anywhere
commonDataStruct = {}
# lock to control access to variable
dataLock = threading.Lock()
# thread handler
yourThread = threading.Thread()
# Database variable
db = SQLAlchemy()


def do_stuff():
    global commonDataStruct
    global yourThread
    with dataLock:
        while True:
            response = requests.get('https://www.lastweektickets.com/')

            if "There are no upcoming tapings." in response.text:
                # Create client
                client = boto3.client(
                    "sns",
                    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                    region_name="us-east-1"
                )

                # Get all number to send notification to
                # from app.ticket_notifier.models.user import User
                numbers = ["3154300461"]#User.get_mobile_numbers()
                for n in numbers:
                    # TODO add logic if number is added another way than just area code + number
                    if len(n) is 10:
                        client.publish(
                            PhoneNumber="+1" + n,
                            Message="Hello World!"
                        )


def do_stuff_start():
    # Do initialisation stuff here
    global yourThread
    # Create your thread
    yourThread = threading.Timer(POOL_TIME, do_stuff, ())
    yourThread.start()


def create_app(config_name="development"):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "HEAD", "POST", "OPTIONS", "PUT", "PATCH", "DELETE"], "expose_headers": "Authorization"}})
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY="dev",
    )

    app.config.from_object(app_config[config_name])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Set logging
    if app.config.get("LOG_LEVEL") is not None and app.config.get("LOG_LOCATION") is not None:
        formatter = logging.Formatter(
            "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
        handler = RotatingFileHandler(app.config['LOG_LOCATION'], maxBytes=100000000, backupCount=1)
        handler.setLevel(app.config["LOG_LEVEL"])
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)

    # register the database commands with SQLAlchemy
    db.init_app(app)

    # set strict_slashes to False, endpoints like /sales_data/upload and /sales_data/upload/ will map to the same thing
    app.url_map.strict_slashes = False

    # apply the blueprints to the app
    from .views.register import register_bp

    app.register_blueprint(register_bp)

    # Start thread to check site
    do_stuff_start()

    return app
