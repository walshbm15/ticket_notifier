import os


class Config(object):
    """Parent configuration class."""
    DEBUG = False
    CSRF_ENABLED = True
    SECRET = os.getenv('SECRET')
    DATABASE_URL = os.getenv('DATABASE_URL')


class DevelopmentConfig(Config):
    """Configurations for Development."""
    DEBUG = True
    SECRET = 'dev'
    DATABASE_URL = os.getenv('DATABASE_URL')
    LOG_LEVEL = "DEBUG"
    LOG_LOCATION = "app/instance/app.log"


class TestingConfig(Config):
    """Configurations for Testing, with a separate test database."""
    TESTING = True
    DEBUG = True
    SECRET = 'test'
    instance_dir = os.path.dirname(os.path.abspath(__file__))
    DATABASE_URL = "sqlite:///{}".format(os.path.join(instance_dir, "sqlite.db"))


app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig
}