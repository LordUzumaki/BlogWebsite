# Import necessary classes and functions from the flask_sqlalchemy, flask_bcrypt, and flask_login packages
from flask_sqlalchemy import SQLAlchemy  # Import the SQLAlchemy class for database interactions
from flask_bcrypt import Bcrypt  # Import the Bcrypt class for password hashing
from flask_login import LoginManager
# Import various utilities and classes from flask_login for user session management

# Initialize a new SQLAlchemy instance which will be used to interact with the database
db = SQLAlchemy()

# Initialize a new Bcrypt instance which will be used for hashing passwords
bcrypt = Bcrypt()

# Initialize a new LoginManager instance which will handle user session management
login_manager = LoginManager()

# Set the default login view to 'login', meaning that any route requiring authentication will redirect to the 'login' route if the user is not authenticated
login_manager.login_view = 'login'

# Set the default flash message category to 'info' for messages displayed by Flask-Login
login_manager.login_message_category = 'info'
