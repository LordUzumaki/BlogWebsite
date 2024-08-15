import os
from functools import wraps
from datetime import datetime
from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from config import Config
from flask_wtf import FlaskForm
from wtforms import SubmitField
from flask_migrate import Migrate
from extensions import db, login_manager
from flask_bcrypt import Bcrypt
from model import Post, User

# Initialize Flask application
app = Flask(__name__, template_folder='templates')
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager.init_app(app)
migrate = Migrate(app, db)

# Flask-WTF form for removing permissions
class RemovePermissionsForm(FlaskForm):
    submit = SubmitField('Remove Permissions')

# Print the template folder path for debugging purposes
print(f"Templates folder: {os.path.join(app.root_path, 'templates')}")

# Flask-Login user loader callback
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Custom decorator to restrict access to admins only
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)  # Forbidden access if the user is not an admin
        return f(*args, **kwargs)
    return decorated_function

# Function to create an admin user if one doesn't already exist
def create_admin_user():
    with app.app_context():
        existing_admin = User.query.filter_by(email='admin@example.com').first()
        if existing_admin:
            print(f"Admin user {existing_admin.username} already exists.")
        else:
            admin_user = User(username='admin', email='admin@example.com', password=bcrypt.generate_password_hash('adminpassword').decode('utf-8'))
            admin_user.is_admin = True
            db.session.add(admin_user)
            db.session.commit()
            print(f"Admin user {admin_user.username} created.")

# Call the function to ensure the admin user is created
create_admin_user()

# Create all database tables
with app.app_context():
    db.create_all()

# Route for the home page, displays all posts
@app.route('/')
@app.route('/home')
def home():
    posts = Post.query.all()  # Retrieve all posts from the database
    return render_template('home.html', posts=posts)

# Route to promote a user to admin (requires admin privileges)
@app.route('/make-admin/<int:user_id>')
@login_required
@admin_required
def make_admin(user_id):
    user = User.query.get_or_404(user_id)
    user.is_admin = True
    db.session.commit()
    flash(f'{user.username} has been promoted to admin!', 'success')
    return redirect(url_for('admin_dashboard'))

# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html')

# Route to log out the user
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

# Admin dashboard route (requires admin privileges)
@app.route('/admin_dashboard')
@login_required
@admin_required
def admin_dashboard():
    form = RemovePermissionsForm()
    users_with_permissions = User.query.filter_by(is_admin=True).all()
    users_without_permissions = User.query.filter_by(is_admin=False).all()
    posts = Post.query.all()
    return render_template('admin_dashboard.html', form=form, users_with_permissions=users_with_permissions, users_without_permissions=users_without_permissions, posts=posts)

# Route to display the user's account page
@app.route('/account')
@login_required
def account():
    return render_template('account.html')

# Route to update the user's account information
@app.route('/account/update/<int:user_id>', methods=['GET', 'POST'])
@login_required
def update_account(user_id):
    user = User.query.get_or_404(user_id)
    if user != current_user:
        abort(403)
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        if request.form['password']:  # If a new password is provided, update it
            user.password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    return render_template('update_account.html', user=user)

# Route to create a new post (requires login)
@app.route('/post/new', methods=['GET','POST'])
@login_required
def new_post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        post = Post(title=title, content=content, author=current_user)
        try:
            db.session.add(post)
            db.session.commit()
            flash('Your post has been created!', 'success')
            return redirect(url_for('new_post'))
        except Exception as e:
            db.session.rollback()
            error_str = str(e.__dict__['orig'])  # Get the original error message
            flash(f'There was an issue creating your post: {error_str}', 'danger')
    return render_template('create_post.html', title='New Post')

# Route to view a specific post by ID
@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('view_post.html', title=post.title, post=post)

# Route to update a post (requires login)
@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    return render_template('edit_post.html', title='Update Post', post=post)

# Route to add a test user (for testing purposes)
@app.route('/add_test_user')
def add_test_user():
    test_user = User(username='testuser', email='testuser@example.com', password=bcrypt.generate_password_hash('password').decode('utf-8'))
    db.session.add(test_user)
    db.session.commit()
    return "Test user added!"

@app.route('/delete-user/<int:user_id>')
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if len(user.posts) > 0:
        flash('User cannot be deleted as they have posts associated with them.', 'danger')
        return redirect(url_for('admin_dashboard'))
    db.session.delete(user)
    db.session.commit()
    flash('User has been deleted!', 'success')
    return redirect(url_for('admin_dashboard'))




# Route to remove admin permissions from a user (requires admin privileges)
@app.route('/remove_permissions/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def remove_permissions(user_id):
    user = User.query.get_or_404(user_id)
    user.is_admin = False
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

# Route to delete a post (requires login)
@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

# Entry point of the application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure database tables are created before the app starts
    app.run(debug=True, host='0.0.0.0', port=5500)
