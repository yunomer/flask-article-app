# https://www.youtube.com/watch?v=addnlzdSQs4&t=15s
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from data import Articles
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

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
def articles():
    return render_template('articles.html', articles = Articles)

@app.route('/article/<string:id>/')
def article(id):
    return render_template('article.html', id=id)

class RegisterForm(Form):
    name = StringField('Name', [validators.length(min=1,max=50)])
    username = StringField('Username', [validators.length(min=4, max=25)])
    email = StringField('Email', [validators.length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')  
    ])
    confirm = PasswordField('Confirm Password')
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
                app.logger.info('PASSWORD MATCHED')

    return render_template('login.html')

if __name__ == '__main__':
    app.secret_key='hello123'
    app.run(debug=True)