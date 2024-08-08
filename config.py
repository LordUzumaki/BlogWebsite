import os  # Import the os module to interact with the operating system

class Config:
    # SECRET_KEY is used for securely signing the session cookie and can be used for other security-related needs.
    # It retrieves the value from the environment variable 'SECRET_KEY' if it exists, otherwise it defaults to 'a_hard_to_guess_string'.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_hard_to_guess_string'

    # SQLALCHEMY_DATABASE_URI sets the database URI that should be used for the connection.
    # It retrieves the value from the environment variable 'DATABASE_URL' if it exists, otherwise it defaults to using a SQLite database file named 'site.db'.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'

    # SQLALCHEMY_TRACK_MODIFICATIONS is set to False to disable tracking modifications of objects and emitting signals.
    # This is for performance reasons as it adds significant overhead.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
