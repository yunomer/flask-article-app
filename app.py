# https://www.youtube.com/watch?v=addnlzdSQs4&t=15s
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from data import Articles
from functools import wraps
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)

# config mySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Canada@17687'
app.config['MYSQL_DB'] = 'myFlaskApp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Initialize MYSQL
mysql = MySQL(app)

Articles = Articles()

# Home page
@app.route('/')
def index():
    return render_template('home.html')

# About
@app.route('/about')
def about():
    return render_template('about.html')

# Articles 
@app.route('/articles')
def articles():
    return render_template('articles.html', articles = Articles)

# Single Article
@app.route('/article/<string:id>/')
def article(id):
    return render_template('article.html', id=id)

# Register form class
class RegisterForm(Form):
    name = StringField('Name', [validators.length(min=1,max=50)])
    username = StringField('Username', [validators.length(min=4, max=25)])
    email = StringField('Email', [validators.length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')  
    ])
    confirm = PasswordField('Confirm Password')

# User register
# https://stackoverflow.com/questions/39281594/error-1698-28000-access-denied-for-user-rootlocalhost
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        # Create Cursor for mysql
        cur = mysql.connection.cursor()
        # Execute the query
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))
        # Commit to the database now
        mysql.connection.commit()
        # Close the connection now
        cur.close()
        flash('You are now Registered and can log in', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form fields
        username = request.form['username']
        password_candidate = request.form['password']

        # create Cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        # if there are results found
        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # now compare the passwords
            if sha256_crypt.verify(password_candidate, password):
                # passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # close the connection after done checking user existance
            cur.close
        else:
            # close the connection after done checking user existance
            cur.close
            error = 'Username or password does not match'
            return render_template('login.html', error=error)

    return render_template('login.html')

# Check if the user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# user logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

# Dashboard 
@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')

# Article form class
class ArticleForm(Form):
    title = StringField('Title', [validators.length(min=1,max=200)])
    body = TextAreaField('Body', [validators.length(min=10)])

# Add Article 
@app.route('/add_article' methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.menthod == 'POST' and form.validate()
        title = form.title.data
        body = form.body.data

        # create the cursor
        cur = mysql.connection.cursor()
        # Execute
        cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)", (title, body, session['username']))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()
        flash('Article Created', 'success')
        return redirect(url_for('dashboard.html'))

    return render_template('add_article', form=form)

if __name__ == '__main__':
    app.secret_key='hello123'
    app.run(debug=True)