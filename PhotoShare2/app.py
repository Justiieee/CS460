######################################
# author ben lawson <balawson@bu.edu> 
# Edited by: Baichuan Zhou (baichuan@bu.edu) and Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from 
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask.ext.login as flask_login

# for image uploading
# from werkzeug import secure_filename
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

# These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '960212'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

# begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email FROM User")
users = cursor.fetchall()


def getUserList():
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM User")
    return cursor.fetchall()


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    users = getUserList()
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    users = getUserList()
    email = request.form.get('email')
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
    data = cursor.fetchall()
    pwd = str(data[0][0])
    user.is_authenticated = request.form['password'] == pwd
    return user


'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
    # The request method is POST (page is recieving data)
    email = flask.request.form['email']
    cursor = conn.cursor()
    # check if email is registered
    if cursor.execute("SELECT password FROM User WHERE email = '{0}'".format(email)):
        data = cursor.fetchall()
        pwd = str(data[0][0])
        if flask.request.form['password'] == pwd:
            user = User()
            user.id = email
            flask_login.login_user(user)  # okay login in user
            return flask.redirect(flask.url_for('protected'))  # protected is a function defined in this file

    # information did not match
    return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('hello.html', message='Logged out')


@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')


# you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
    return render_template('register.html', supress='True')


@app.route("/register", methods=['POST'])
def register_user():
    try:
        fname = request.form.get('first_name')
        lname = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        gender = request.form.get('gender')
        dob = request.form.get('date_of_birth')
        hometown = request.form.get('hometown')
    except:
        print("couldn't find all tokens")  # this prints to shell, end users will not see this (all print statements go to shell)
        return flask.redirect(flask.url_for('register'))
    cursor = conn.cursor()
    test = isEmailUnique(email)
    if test:
        print("INSERT INTO User (fname, lname, email, password, gender, dob, hometown) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')".format(fname, lname, email, password, gender, dob, hometown))
        cursor.execute("INSERT INTO User (fname, lname, email, password, gender, dob, hometown) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')".format(fname, lname, email, password, gender, dob, hometown))
        conn.commit()
        # log user in
        user = User()
        user.id = email
        flask_login.login_user(user)
        return render_template('hello.html', name=email, message='Account Created!!!!!!')
    else:
        print("couldn't find all tokens")
        return flask.redirect(flask.url_for('register'))

@app.route('/friends', methods=['GET', 'POST'])
@flask_login.login_required
def add_friend():
    if request.method == 'POST':
        try:
            email = request.form.get('friends_email')
            uid1 = getUserIdFromEmail(flask_login.current_user.id)
            uid2 = getUserIdFromEmail(email)
        except:
            #print("It is not a user.")
            #return flask.redirect(flask.url_for('add_friend'))
            return render_template('hello.html', name=flask_login.current_user.id, message='Not a user')

            #return render_template('hello.html', name=flask_login.current_user.id, message='Search another friend')
        test1 = isaUser(email)
        if test1:
            cursor = conn.cursor()
            test2 = isaFriend(uid1, uid2)
            print(test2)
            if test2:
                print("INSERT INTO Friendship (user_id1, user_id2) VALUES ('{0}', '{1}')".format(uid1, uid2))
                cursor.execute(
                    "INSERT INTO Friendship (user_id1, user_id2) VALUES ('{0}', '{1}')".format(uid1, uid2))
                cursor.execute(
                    "INSERT INTO Friendship (user_id1, user_id2) VALUES ('{0}', '{1}')".format(uid2, uid1))
                conn.commit()
                return render_template('hello.html', name=flask_login.current_user.id, message='Friend Added')
            else:
                return render_template('hello.html', name=flask_login.current_user.id, message='Already friended. Search for another friend')
        else:
            return render_template('hello.html', name=flask_login.current_user.id, message='He/She is not a user! Please invite you friend')
    else:
        return render_template('friends.html')

@app.route('/friendList', methods=['GET', 'POST'])
@flask_login.login_required
def friend_list():
    if request.method == 'POST':
        try:
            uid=getUserIdFromEmail(flask_login.current_user.id)
            print(uid)
        except:
            return render_template('friendList', name=flask_login.current_user.id, message='Here is your friend list')
            #return flask.redirect(flask.url_for('friend_list'))
        cursor = conn.cursor()
        print(cursor.execute("SELECT user_id2 FROM Friendship WHERE user_id2='uid'"))
        conn.commit()
    else:
        return render_template('friendList.html')


@app.route('/album', methods=['GET', 'POST'])
@flask_login.login_required
def create_album():
    if request.method == 'POST':
        try:
            aname = request.form.get('name')
            date_creation = request.form.get('date_creation')
            user_id = getUserIdFromEmail(flask_login.current_user.id)
            print(user_id)
        except:
            #print("It is not a user.")
            #return flask.redirect(flask.url_for('add_friend'))
            #return render_template('hello.html', name=flask_login.current_user.id, message='')
            return flask.redirect(flask.url_for('create_album'))
        cursor = conn.cursor()
        test = isanAlbum(aname)
        print(test)
        if test:
            print("INSERT INTO Album (name, date_creation, user_id) VALUES ('{0}', '{1}', '{2}')".format(aname, date_creation, user_id))
            cursor.execute("INSERT INTO Album (name, date_creation, user_id) VALUES ('{0}', '{1}', '{2}')".format(aname, date_creation, user_id))
            conn.commit()
            return render_template('hello.html', name=flask_login.current_user.id, message='Album Created!')
        else:
            return render_template('hello.html', name=flask_login.current_user.id, message='Album Existed')
    else:
        return render_template("createAlbum.html")
        #return flask.redirect(flask.url_for('create_album'))

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def show_album():
    if request.method == 'POST':
        try:
            uid = getUserIdFromEmail(flask_login.current_user.id)
        except:
            return flask.redirect(flask.url_for('show_album'))
        cursor = conn.cursor()
        print(cursor.execute("SELECT name, date_creation FROM album WHERE user_id = 'uid'"))
        conn.commit()
        return render_template('showAlbum.html')
    else:
        return render_template('showAlbum.html')




@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
    if request.method == 'POST':
        uid = getUserIdFromEmail(flask_login.current_user.id)
        imgfile = request.files['photo']
        caption = request.form.get('caption')
        print(caption)
        photo_data = base64.standard_b64encode(imgfile.read())
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Photo (imgdata, user_id, caption) VALUES ('{0}', '{1}', '{2}' )".format(photo_data, uid, caption))
        conn.commit()
        return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!',
                               photos=getUserPhotos(uid))
    # The method is GET so we return a  HTML form to upload the a photo.
    else:
        return render_template('upload.html')





#small method
def getUserPhotos(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT imgdata, photo_id, caption FROM Photo WHERE user_id = '{0}'".format(uid))
    return cursor.fetchall()  # NOTE list of tuples, [(imgdata, pid), ...]


def getUserIdFromEmail(email):
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM User WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]

def getUserIdFromAlbum(name):
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM Album WHERE name = '{0}'".format(name))
    return cursor.fetall()

def isEmailUnique(email):
    # use this to check if a email has already been registered
    cursor = conn.cursor()
    if cursor.execute("SELECT email  FROM User WHERE email = '{0}'".format(email)):
        # this means there are greater than zero entries with that email
        return False
    else:
        return True

def isaUser(email):
    cursor = conn.cursor()
    if cursor.execute("SELECT email FROM User"):
        return True
    else:
        return False

def isaFriend(uid1, uid2):
    cursor = conn.cursor()
    if cursor.execute("SELECT user_id1 FROM Friendship WHERE user_id1='uid1'") and cursor.execute("SELECT user_id2 FROM Friendship WHERE user_id2='uid2'"):
        return True
    else:
        return False

def isanAlbum(aname):
    cursor = conn.cursor()
    if cursor.execute("SELECT name FROM Album WHERE name='aname' "):
        return True
    else:
        return False
# end login code

@app.route('/profile')
@flask_login.login_required
def protected():
    return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile")


# begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS






# end photo uploading code


# default page
@app.route("/", methods=['GET'])
def hello():
    return render_template('hello.html', message='Welecome to Photoshare')


if __name__ == "__main__":
    # this is invoked when in the shell  you run
    # $ python app.py
    app.run(port=5000, debug=True)
