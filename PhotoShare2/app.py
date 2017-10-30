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

#need to revise: 1. can not add yourself as a friend; 2.leave comment when you are not logged in;


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
app.config['MYSQL_DATABASE_PASSWORD'] = '950205aa'
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
            return render_template('friendList.html', name=flask_login.current_user.id, message='Not a user')

            #return render_template('hello.html', name=flask_login.current_user.id, message='Search another friend')
        #test1 = isaUser(email)
        #if test1:
        cursor = conn.cursor()
        test2 = isaFriend(uid1, uid2)
        print(test2)
        if not test2:
            print("INSERT INTO Friendship (user_id1, user_id2) VALUES ('{0}', '{1}')".format(uid1, uid2))
            cursor.execute(
                "INSERT INTO Friendship (user_id1, user_id2) VALUES ('{0}', '{1}')".format(uid1, uid2))
            cursor.execute(
                "INSERT INTO Friendship (user_id1, user_id2) VALUES ('{0}', '{1}')".format(uid2, uid1))
            conn.commit()
            return render_template('profile.html', name=flask_login.current_user.id, message='Friend Added')
        else:
            return render_template('profile.html', name=flask_login.current_user.id, message='Already friended. Search for another friend')
        #else:
            #return render_template('hello.html', name=flask_login.current_user.id, message='He/She is not a user! Please invite you friend')
    else:
        return render_template('profile.html')

@app.route('/friendList', methods=['GET'])
@flask_login.login_required
def friend_list():
    uid=getUserIdFromEmail(flask_login.current_user.id)
    print(uid)
    friendlist = getUserFriends(uid)
    print(friendlist)
    #friendname= getUserNameFromId()
    #print(friendname)
    return render_template('friendList.html',message = 'Here is your friendlist', friends = friendlist)


@app.route('/createAlbum', methods=['GET', 'POST'])
@flask_login.login_required
def create_album():
    if request.method == 'POST':
        try:
            aname = request.form.get('name')
            date_creation = request.form.get('date_creation')
            uid = getUserIdFromEmail(flask_login.current_user.id)
            print(uid)
        except:
            return flask.redirect(flask.url_for('createAlbum'))
        cursor = conn.cursor()
        test = isanAlbum(uid,aname)
        print(test)
        if not test:
            print("INSERT INTO Album (name, date_creation, user_id) VALUES ('{0}', '{1}', '{2}')".format(aname, date_creation, uid))
            cursor.execute("INSERT INTO Album (name, date_creation, user_id) VALUES ('{0}', '{1}', '{2}')".format(aname, date_creation, uid))
            conn.commit()
            return render_template('showAlbum.html', name=flask_login.current_user.id, message='Album Created!')
        else:
            return render_template('createAlbum.html', name=flask_login.current_user.id, message='Album Existed!')
    else:
        return render_template("createAlbum.html", supress = 'True')


@app.route('/showAlbum', methods=['GET'])
@flask_login.login_required
def show_album():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    print(uid)
    albumlist = getUserAlbum(uid)
    print(albumlist)
    return render_template('showAlbum.html', message = 'Here is your Album list', albums = albumlist)

@app.route('/guest', methods = ['GET'])
def guest():
    allalbum = getAllAlbums()
    print(allalbum)
    return render_template('guest.html', message = 'Public albums', allalbums = allalbum)




@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
    if request.method == 'POST':
        try:
            uid = getUserIdFromEmail(flask_login.current_user.id)
            imgfile = request.files['photo']
            caption = request.form.get('caption')
            aname = request.form.get('album')
            album_id = getAlbumIdFromAlbumName(aname)
            photo_data = base64.standard_b64encode(imgfile.read())


        except:
            return render_template('createAlbum.html', message='You do not have this album. Please create an album')
        test = isAlbumYourself(uid,album_id)
        if test:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Photo (imgdata, user_id, caption, album_id) VALUES ('{0}', '{1}', '{2}','{3}' )".format(photo_data, uid, caption, album_id))

            conn.commit()
            return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!',
                               photos=getUserPhotos(uid))
        else:
            return render_template('upload.html', message='You Can Only Upload Photos To Your Own Albums')
    # The method is GET so we return a  HTML form to upload the a photo.
    else:
        return render_template('upload.html')

@app.route('/photo', methods=['GET', 'POST'])
def photo():
    if request.method == 'POST':
        aid = request.form.get('album_id')
        print(aid)
        photoList=getPhotoFromAlbumId(aid)
        return render_template('photo.html', message = 'Here are Photos', photos = photoList)
    else:
        return render_template('photo.html')

@app.route('/deletePhoto',methods = ['GET', 'POST'])
@flask_login.login_required
def delete_photo():
    if request.method == 'POST':
        pid = request.form.get('delete')
        uid = getUserIdFromEmail(flask_login.current_user.id)

        test = isPhotoYourself(uid, pid)
        if test:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Photo WHERE photo_id = '{0}'".format(pid))
            conn.commit()
            return render_template('photo.html', message = 'Photo Deleted')
        else:
            return render_template('photo.html', message = 'You Can Only Delete Your Photos')
    else:
        return render_template('photo.html')

@app.route('/deleteAlbum', methods=['GET', 'POST'])
@flask_login.login_required
def delete_album():
    if request.method == 'POST':
        aid = request.form.get('delete_album')
        #print aid
        uid = getUserIdFromEmail(flask_login.current_user.id)
        test = isAlbumYourself(uid, aid)
        if test:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Album WHERE album_id = '{0}'".format(aid))
            cursor.execute("DELETE FROM Photo WHERE album_id = '{0}'".format(aid))
            conn.commit()
            return render_template('hello.html', message='Album Deleted')
        else:
            return render_template('showAlbum.html', message = 'You Can Only Delete Your Album')
    else:
        return render_template('showAlbum.html')

@app.route('/comment', methods=['GET', 'POST'])
def comment():
    if request.method == 'POST':
        content = request.form.get('content')
        date_creation = request.form.get('date_creation')
        uid = getUserIdFromEmail(flask_login.current_user.id)
        #print uid
        pid = request.form.get('photo_id')
        #print pid
        test = isPhotoYourself(uid,pid)
        #print(test)
        if not test:
            cursor=conn.cursor()
            cursor.execute("INSERT INTO Comment (content, date_creation, user_id, photo_id) VALUES ('{0}','{1}', '{2}', '{3}')".format(content, date_creation, uid, pid))
            conn.commit()
            return render_template('photo.html', message='Commented successfully')
        else:
            return render_template('comment.html', message='You can not comment on your photos')
    else:
        return render_template('comment.html')

@app.route('/showComment', methods=['GET', 'POST'])
def show_comment():
    if request.method == 'POST':
        pid = request.form.get('photo_id')
        commentList = getCommentFromPhotoId(pid)
        #print commentList
        return render_template('showComment.html', message = 'Here are the comments', comments = commentList)
    else:
        return render_template('showComment.html')

@app.route('/like', methods=['GET', 'POST'])
@flask_login.login_required
def liketable():
    if request.method == 'POST':
        pid = request.form.get('photo_id')
        date_creation = request.form.get('date_creation')
        uid = getUserIdFromEmail(flask_login.current_user.id)
        #print uid
        #print pid
        test = isLikeExist(uid, pid)
        if not test:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Liketable (user_id, photo_id, date_creation) VALUES ('{0}','{1}', '{2}')".format(uid, pid,date_creation))
            conn.commit()
            return render_template('like.html', message='Like successfully')
        else:
            return render_template('like.html', message = 'Already Like')

    else:
        return render_template('like.html')

@app.route('/showLike', methods=['GET','POST'])
@flask_login.login_required
def showLike():
    if request.method == 'POST':
        pid=request.form.get('photo_id')
        #count = getCountLike(pid)[1]
        #print(count)
        cursor=conn.cursor()
        likeList=getUserIdForLike(pid)
        countList=getCountForUserLike(pid)
        print(countList)
        print(likeList)

        conn.commit()
        return render_template('showLike.html', message = 'Here is all likers', liketable = likeList, count = countList)
    else:
        return render_template('showLike.html')

@app.route('/tag', methods=['GET', 'POST'])
@flask_login.login_required
def tag():
    if request.method == 'POST':
        hashtag = request.form.get('hashtag')
        pid = request.form.get('photo_id')
        test = isPhotoExist(pid)
        if test:
            cursor = conn.cursor()
            #cursor.execute("INSERT INTO Tag(hashtag) VALUES ('{0}')".format(hashtag))
            cursor.execute("INSERT INTO Associate (photo_id, hashtag) VALUES ('{0}','{1}')".format(pid,hashtag))
            conn.commit()
            return render_template('tag.html',message='Tag Added')
        else:
            return render_template('tag.html', message='Photo does not exist')
    else:
        return render_template('tag.html')


@app.route('/searchTag',methods=['GET', 'POST'])
def searchTag():
    if request.method == 'POST':
        hashtag = request.form.get('hashtag')
        hashtag = hashtag.split(" ")
        photoList = []
        for i in hashtag:
            test = isTagExist(i)
            if test:
                photoList += getAllPhotoFromTag(i)
        if photoList != []:
            return render_template('seeAllPhoto.html', message='Here are all photos', photos=photoList)
        else:
            return render_template('searchTag.html', message = 'Tag does not exist')
    else:
        return render_template('searchTag.html')

@app.route('/searchComments', methods = ['GET', 'POST'])
def searchComments():
    if request.method == 'POST':
        content = request.form.get('content')
        test = isCommentExist(content)
        if test:
            userList = getAllUserFromComment(content)
            print(userList)
            return render_template('searchComments.html', message = 'Users who has this comment', comments = userList)
        else:
            return render_template('searchComments.html', message = 'Comment does not exist')
    else:
        return render_template('searchComments.html')


@app.route('/seeYourPhoto',methods=['GET', 'POST'])
@flask_login.login_required
def seeYourPhoto():
    if request.method == 'POST':
        hashtag = request.form.get('hashtag')
        uid = getUserIdFromEmail(flask_login.current_user.id)
        photoList = getYourPhotoFromTag(hashtag, uid)
        return render_template('seeYourPhoto.html', message = 'Here are your photos for this tag', photos = photoList)
    else:
        return render_template('seeAllPhoto.html')

@app.route('/top10', methods = ['GET'])
def top10Users():
    top10List = getTop10()
    print top10List
    result = []
    for i in top10List:
        cursor = conn.cursor()
        cursor.execute("SELECT fname, lname, user_id FROM User WHERE user_id = '{0}'".format(i))
        result.append(cursor.fetchone())
    return render_template('top10.html', message = 'Here is Top 10 Users', users = result)

@app.route('/mayalsolike', methods = ['GET'])
@flask_login.login_required
def mayalsolike():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    photolist = allphotosfromfivetag(uid)
    result = []
    for i in photolist:
        cursor = conn.cursor()
        cursor.execute("SELECT photo_id, COUNT(photo_id) FROM Associate WHERE photo_id = '{0}' and hashtag = '{1}' or hashtag = '{2}' or hashtag = '{3}' or hashtag='{4}' or hashtag='{5}' GROUP BY photo_id".format(i,top5[0],top5[1],top5[2],top5[3],top5[4]))
        result.append(cursor.fetchone())
    sortresult = sorted(result, key = getKey, reverse = True)
    highest = []
    for a in len(sortresult):
        if (a+1) == len(sortresult):
            highest.append(sortresult[a][0])
        elif sortresult[a][1] > sortresult[a+1][1]:
            highest.append(sortresult[a][0])
        else:
            number = getnumberoftag(sortresult[a][1])
            number2 = getnumberoftag(sortresult[a+1][1])
            if number>number2:
                highest.append(sortresult[a][0])
            else:
                highest.append(sortresult[a+1][0])
    return render_template('mayalsolike.html', message = 'Here is you may also like', photolists = highest)


@app.route('/friendsNameRecommand', methods = ['GET'])
@flask_login.login_required
def friendsNameRecommand():
    friendsName = friendsRecommand()
    print friendsName
    result =[]
    for i in friendsName:
        cursor=conn.cursor()
        cursor.execute("SELECT fname, lname, user_id FROM User WHERE user_id ='{0}'".format(i))
        result.append(cursor.fetchone())
    return render_template('friendsNameRecommand.html', message = 'Here is your recommanded', friends = result)



#get friend id recommanded
def friendsRecommand():
    uid=getUserIdFromEmail(flask_login.current_user.id)
    friendIDCountList = sorted(getRecommandFriend(uid),key =getKey, reverse=True)
    #test if is friends:
    friendIDList = []
    for i in friendIDCountList:
        if not isaFriend(i[0],uid):
            friendIDList.append(i[0])
    return friendIDList



#small method
def getUserPhotos(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT imgdata, photo_id, caption FROM Photo WHERE user_id = '{0}'".format(uid))
    return cursor.fetchall()  # NOTE list of tuples, [(imgdata, pid), ...]

def getPhotoFromAlbumId(aid):
    cursor = conn.cursor()
    cursor.execute("SELECT imgdata, photo_id, caption FROM Photo WHERE album_id = '{0}'".format(aid))
    return cursor.fetchall()

def getUserAlbum(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT album_id, name, date_creation FROM Album WHERE user_id ='{0}'".format(uid))
    return cursor.fetchall()

def getAllAlbums():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Album")
    return cursor.fetchall()


def getUserIdFromEmail(email):
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM User WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]

def getUserIdFromAlbum(name):
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM Album WHERE name = '{0}'".format(name))
    return cursor.fetchall()

def getAlbumIdFromAlbumName(aname):
    cursor=conn.cursor()
    cursor.execute("SELECT album_id FROM Album WHERE name = '{0}'".format(aname))
    return cursor.fetchone()[0]

def getUserFriends(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT user_id1,fname, lname FROM Friendship,User WHERE user_id1 = user_id and user_id2= '{0}'".format(uid))
    return cursor.fetchall()

def getUserNameFromId(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT fname,lname FROM User WHERE user_id = '{0}'".format(uid))
    return cursor.fetchall()

def getCommentFromPhotoId(pid):
    cursor = conn.cursor()
    cursor.execute("SELECT content, user_id FROM Comment WHERE photo_id = '{0}'".format(pid))
    return cursor.fetchall()

def getAllTag():
    cursor=conn.cursor()
    cursor.execute("SELECT hashtag FROM Tag")
    return cursor.fetchall()

def getYourPhotoFromTag(hashtag, uid):
    cursor=conn.cursor()
    cursor.execute("SELECT imgdata, A.photo_id, caption FROM Photo P, Associate A WHERE P.photo_id = A.photo_id and hashtag = '{0}' and user_id = '{1}'".format(hashtag, uid))
    return cursor.fetchall()

def getAllPhotoFromTag(hashtag):
    cursor=conn.cursor()
    cursor.execute("SELECT imgdata, A.photo_id, caption FROM Photo P, Associate A WHERE P.photo_id = A.photo_id and hashtag = '{0}'".format(hashtag))
    return cursor.fetchall()

def getAllUserFromComment(content):
    cursor=conn.cursor()
    cursor.execute("SELECT U.user_id, Count(comment_id) FROM User U, Comment C WHERE C.user_id = U.user_id and content = '{0}' GROUP BY U.user_id ORDER BY COUNT(comment_id) DESC".format(content))
    return cursor.fetchall()


def isEmailUnique(email):
    # use this to check if a email has already been registered
    cursor = conn.cursor()
    if cursor.execute("SELECT email  FROM User WHERE email = '{0}'".format(email)):
        # this means there are greater than zero entries with that email
        return False
    else:
        return True

def isPhotoYourself(uid, pid):
    cursor = conn.cursor()
    if cursor.execute("SELECT photo_id FROM Photo WHERE user_id = '{0}' and photo_id = '{1}'".format(uid, pid)):
        return True
    else:
        return False

def isAlbumYourself(uid, aid):
    cursor = conn.cursor()
    if cursor.execute("SELECT album_id FROM Album WHERE user_id = '{0}' and album_id = '{1}'".format(uid, aid)):
        return True
    else:
        return False

def isaUser(email):
    cursor = conn.cursor()
    if cursor.execute("SELECT email FROM User WHERE email = '{0}'".format(email)):
        return True
    else:
        return False

def isaFriend(uid1, uid2):
    cursor = conn.cursor()
    if cursor.execute("SELECT user_id1 FROM Friendship WHERE user_id1 = '{0}' and user_id2 = '{1}'".format(uid1, uid2)):
        return True
    else:
        return False

def isanAlbum(uid, aname):
    cursor = conn.cursor()
    if cursor.execute("SELECT album_id FROM Album WHERE user_id = '{0}' and name = '{1}'".format(uid, aname)):
        return True
    else:
        return False

def isLikeExist(uid, pid):
    cursor = conn.cursor()
    if cursor.execute("SELECT * FROM Liketable WHERE user_id ='{0}' and photo_id = '{1}'".format(uid, pid)):
        return True
    else:
        return False

def isPhotoExist(pid):
    cursor = conn.cursor()
    if cursor.execute("SELECT * FROM Photo WHERE photo_id='{0}'".format(pid)):
        return True
    else:
        return False
def isTagExist(hashtag):
    cursor=conn.cursor()
    if cursor.execute("SELECT * FROM Associate WHERE hashtag ='{0}'".format(hashtag)):
        return True
    else:
        return False

def isCommentExist(content):
    cursor=conn.cursor()
    if cursor.execute("SELECT content FROM Comment WHERE content = '{0}'".format(content)):
        return True
    else:
        return False

def getCountLike(pid):
    cursor=conn.cursor()
    cursor.execute("SELECT photo_id, COUNT(user_id) FROM Liketable GROUP BY photo_id")
    return cursor.fetchall()

def getUserIdForLike(pid):
    cursor=conn.cursor()
    cursor.execute("SELECT user_id FROM Liketable WHERE photo_id = '{0}'".format(pid))
    return cursor.fetchall()

def getCountForUserLike(pid):
    cursor=conn.cursor()
    cursor.execute("SELECT COUNT(user_id) FROM Liketable WHERE photo_id = '{0}'".format(pid))
    return cursor.fetchall()

def getUserContribution():
    usercontribution = []
    cursor= conn.cursor()
    cursor.execute("SELECT user_id, COUNT(comment_id) FROM Comment GROUP BY user_id")
    for a in cursor:
        usercontribution.append([a[0], a[1]])
    newcursor = conn.cursor()
    newcursor.execute("SELECT user_id, COUNT(photo_id) FROM Photo GROUP BY user_id")
    for b in newcursor:
        for c in usercontribution:
            if b[0] == c[0]:
                c[1] = c[1] + b[1]
            else:
                c[1] = c[1]
    return usercontribution

def getKey(elem):
    return elem[1]

def getTop10():
    usercontribution = getUserContribution()
    top10 = []
    orderUsers = sorted(usercontribution, key = getKey, reverse = True)
    if len(orderUsers) <= 10:
        for a in orderUsers:
            top10.append(a[0])
        return top10
    else:
        result = orderUsers[0:10]
        for b in result:
            top10.append(b[0])
        return top10

def userTag(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT hashtag, COUNT(hashtag) FROM Associate A, Photo P WHERE A.photo_id=P.photo_id and P.user_id = '{0}' GROUP BY hashtag".format(uid))
    return cursor.fetchall()


def topfivetag(uid):
    taglist = userTag(uid)
    top5 = []
    orderTag = sorted(taglist, key = getKey, reverse = True)
    if len(orderTag) <= 5:
        for x in orderTag:
            top5.append(x[0])
        return top5
    else:
        result = orderTag[0:5]
        for y in result:
            top5.append(y[0])
        return top5

def allphotosfromfivetag(uid):
    fivetag = topfivetag(uid)
    allphoto = []
    for i in fivetag:
        allphoto.append(getAllPhotoFromTag(i))
    return allphoto

def getnumberoftag(pid):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(photo_id) FROM Associate WHERE photo_id = '{0}'".format(pid))
    return cursor.fetchall()

#get friend with common friend, not test if its friends
def getRecommandFriend(uid):
    cursor=conn.cursor()
    cursor.execute("SELECT F2.user_id2, COUNT(F2.user_id2) FROM Friendship F1, Friendship F2 WHERE F1.user_id1 = F2.user_id1 AND F1.user_id2 <> F2.user_id2 AND F1.user_id2 = '{0}' GROUP BY F2.user_id2".format(uid))
    return cursor.fetchall()
# end login code

@app.route('/profile')
@flask_login.login_required
def protected():
    return render_template('profile.html', name=flask_login.current_user.id, message="Here's your profile")


# begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS





# end photo uploading code

# default page
@app.route("/", methods=['GET'])
def hello():
    return render_template('hello.html', message='Welcome to Photoshare')


if __name__ == "__main__":
    # this is invoked when in the shell  you run
    # $ python app.py
    app.run(port=5000, debug=True)
