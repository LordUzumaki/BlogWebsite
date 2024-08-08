import os
from flask import Flask, render_template, url_for, flash, redirect, request, abort
from flask_migrate import Migrate

from config import Config
from extensions import db, bcrypt, login_manager
from model import User, Post
from flask_login import login_user,  current_user, logout_user, login_required, login_user



app = Flask(__name__, template_folder='templates')
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)
migrate = Migrate(app, db)

# Print the template folder path to verify it's correct
print(f"Templates folder: {os.path.join(app.root_path, 'templates')}")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()  # Ensure database tables are created




#Define the route for the home page

@app.route('/')
@app.route('/home')
def home():
    #Retrieve all posts from the database
    posts = Post.query.all()
    #Renders the home tamplate and pass the posts to it
    return render_template('home.html', posts=posts)



#Define the route for the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    #If the user is already authenticated, redirect home
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    #If the form is submitted
    if request.method == 'POST':
        #Get the form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        #Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        #Create a new user instance
        user = User(username=username, email=email, password=hashed_password)
        #add the user to the database
        db.session.add(user)
        #Commit the changes to the database
        db.session.commit()
        #Flash a success message
        flash('Your account has been created! Your are now able to log in', 'success')
        #redirect to login page
        return redirect(url_for('login'))
    #Render the registration template
    return render_template('register.html')





#Define the route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    #If the user already authenticated, redirect to home
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    #If the form is submitted
    if request.method == 'POST':
        #Get the form data
        email = request.form.get('email')
        password = request.form.get('password')
        #Retrieve the user from the database by email
        user = User.query.filter_by(email=email).first()
        #Check if the user exists and the password is correct
        if user and bcrypt.check_password_hash(user.password, password):
            #log the user in
            login_user(user)
            #Get the next page if it exists, otherwise redirect to home
            next_page = request.args.get('next')
            
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            #Flash an error message if login is unsucessful
            flash('Login Unsuccessful. Please check email and password', 'danger')
    #render the login template
    return render_template('login.html')




#Define the route for logging out
@app.route('/logout')
def logout():
    #Log the user out
    logout_user()
    #Redirect to the home page
    return redirect(url_for('home'))




#Define the route for the account page (requires login)
@app.route('/account')
@login_required
def account():
    #Render the account template
    return render_template('account.html')




#Define the route for creating a new post (requires login)
@app.route('/post/new', methods=['GET','POST'])
@login_required
def new_post():
    #if the form is submitted
    if request.method == 'POST':
        #Get the form data
        title = request.form.get('title')
        content = request.form.get('content')
        #Create a new post instance
        post = Post(title=title, content=content, author=current_user)
        #add the post to the database
        db.session.add(post)
        db.session.commit()
        #Flash a success message
        flash('Your post has been created!', 'success')
        #Redirect to the home page
        return redirect(url_for('home'))
    #Render the create post template
    return render_template('create_post.html', title='New Post')




#Define the route for viewing a post by its ID
@app.route('/post/<int:post_id>')
def post(post_id):
    #Retrieve the post by its ID
    post = Post.query.get_or_404(post_id)
    #Render the view post template and pass the post to it
    return render_template('view_post.html', title=post.title, post=post)




#Define the route for updating a post by its ID(requires login)
@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    #Retrieve the post by its ID
    post = Post.query.get_or_404(post_id)  # Corrected the typo here
    #Ensure the current user is the author of the post
    if post.author != current_user:
        abort(403)
    #if the form is submitted
    if request.method == 'POST':
        #update the post date
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        #Commit the changes to the database
        db.session.commit()
        #Flash a success message
        flash('Your post has been updated!', 'success')
        #Redirct to the updated post page
        return redirect(url_for('post', post_id=post.id))
    #render the updatre post template and pass the post to it
    return render_template('create_post.html', title='Update Post', post=post)




#Define the route for deleting a post by its ID (requires login)
@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    #Retrieve the post by its ID
    post = Post.query.get_or_404(post_id)  # Corrected the typo here
    #Ensure the currect user is the author of the post
    if post.author != current_user:
        abort(403)
    #Delete the post from the database
    db.session.delete(post)
    #Commit the changes to the database
    db.session.commit()
    #Flash a success message
    flash('Your post has been deleted!', 'success')
    #Redirect to the home page
    return redirect(url_for('home'))



#Entry point of the application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5500)
