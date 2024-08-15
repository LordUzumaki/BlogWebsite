from datetime import datetime # Import the datetime class to handle date and time
from extensions import db  # Import the db instance from the extensions module
from flask_login import UserMixin  # Import UserMixin to add default implementations for user authentication
from sqlalchemy.orm import relationship
# Define the User class, which represents users in the database
class User(db.Model, UserMixin):  # Inherit from db.Model and UserMixin
    # Define columns for the User table
    id = db.Column(db.Integer, primary_key=True)  # Primary key column
    username = db.Column(db.String(20), unique=True, nullable=False)  # Username column, must be unique and not null
    email = db.Column(db.String(120), unique=True, nullable=False)  # Email column, must be unique and not null
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')  # Image file column, default value is 'default.jpg'
    date_joined = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    password = db.Column(db.String(60), nullable=False)  # Password column, not null
    posts = relationship('Post', backref='author', lazy=True, cascade="all, delete-orphan")  # One-to-many relationship with Post
    is_admin = db.Column(db.Boolean, default=False)  # New field
    # Define how the User object is printed
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

# Define the Post class, which represents posts in the database
class Post(db.Model):  # Inherit from db.Model
    # Define columns for the Post table
    id = db.Column(db.Integer, primary_key=True)  # Primary key column
    title = db.Column(db.String(100), nullable=False)  # Title column, not null
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Date posted column, default value is current time
    content = db.Column(db.Text, nullable=False)  # Content column, not null
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key column, references User table

    # Define how the Post object is printed
    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"
